"""Assignment 3 - Cleaned and Fixed Version."""

# Standard library
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
import gc

import matplotlib.pyplot as plt
import mujoco as mj
import random
import numpy as np
import numpy.typing as npt
from mujoco import viewer
from deap import base, creator, tools

# Local libraries
from ariel import console
from ariel.body_phenotypes.robogen_lite.constructor import (
    construct_mjspec_from_graph,
)
from ariel.body_phenotypes.robogen_lite.decoders.hi_prob_decoding import (
    HighProbabilityDecoder,
    save_graph_as_json,
)
from ariel.ec.genotypes.nde import NeuralDevelopmentalEncoding
from ariel.simulation.controllers.controller import Controller
from ariel.simulation.environments import OlympicArena
from ariel.utils.renderers import single_frame_renderer, video_renderer
from ariel.utils.runners import simple_runner
from ariel.utils.tracker import Tracker
from ariel.utils.video_recorder import VideoRecorder

# Type Checking
if TYPE_CHECKING:
    from networkx import DiGraph

# Type Aliases
ViewerTypes = Literal["launcher", "video", "simple", "no_control", "frame"]

# --- RANDOM GENERATOR SETUP --- #
SEED = 42
RNG = np.random.default_rng(SEED)

# --- DATA SETUP ---
SCRIPT_NAME = __file__.split("/")[-1][:-3]
CWD = Path.cwd()
DATA = CWD / "__data__" / SCRIPT_NAME
DATA.mkdir(exist_ok=True)

# Global variables
SPAWN_POS = [-0.8, 0, 0.25]
NUM_OF_MODULES = 30
SIMULATION_DURATION = 15  # Longer duration to traverse terrain
NDE = NeuralDevelopmentalEncoding(number_of_modules=NUM_OF_MODULES)

# EA setup
toolbox = base.Toolbox()
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("BrainIndividual", list, fitness=creator.FitnessMax)
creator.create("BodyIndividual", list, fitness=creator.FitnessMax, best_brain=None)

# EA parameters
BRAIN_HIDDEN_SIZE = 8
BRAIN_GENERATIONS = 100
BRAIN_POPULATION_SIZE = 200
BRAIN_CROSSOVER_PROBABILITY = 0.5
BRAIN_MUTATION_PROBABILITY = 0.2
BRAIN_NUMBER_OF_ELITES = 5

BODY_GENERATIONS = 100
BODY_POPULATION_SIZE = 200
BODY_CROSSOVER_PROBABILITY = 0.5
BODY_MUTATION_PROBABILITY = 0.2
BODY_NUMBER_OF_ELITES = 5

# Body genome setup
BODY_GENOME_LENGTH = 64 * 3  # NDE requires 3 matrices of 64 values each


def fitness_function(history: list[float]) -> float:
    """
    Calculate fitness based on:
    1. Forward distance traveled (primary objective)
    2. Speed of movement (efficiency bonus)
    3. Stability penalty (avoid erratic movement or falling)
    """
    if not history or len(history) < 2:
        return -1000.0  # Penalty for failed simulation
    
    pos_array = np.array(history)
    
    # 1. Total forward distance (X-axis) - PRIMARY METRIC
    start_x = pos_array[0, 0]
    end_x = pos_array[-1, 0]
    forward_distance = end_x - start_x
    
    # 2. Average speed (distance per time step) - EFFICIENCY
    total_distance = 0
    for i in range(1, len(pos_array)):
        step_dist = np.linalg.norm(pos_array[i] - pos_array[i-1])
        total_distance += step_dist
    avg_speed = total_distance / len(pos_array)
    
    # 3. Stability check - penalize if robot falls (z < 0.05)
    min_height = np.min(pos_array[:, 2])
    stability_penalty = 0
    if min_height < 0.05:
        stability_penalty = -50  # Robot fell or got stuck
    
    # 4. Check for getting stuck (low movement variance)
    x_variance = np.var(pos_array[:, 0])
    if x_variance < 0.001:  # Robot barely moved
        return -100.0
    
    # Combined fitness: prioritize forward progress, reward speed, penalize instability
    fitness = (
        forward_distance * 10.0 +      # Main objective: go far
        avg_speed * 5.0 +               # Bonus: move efficiently
        stability_penalty               # Penalty: avoid falling
    )
    
    return fitness


def show_xpos_history(history: list[float]) -> None:
    """Visualize robot trajectory on arena background."""
    # Create a tracking camera
    camera = mj.MjvCamera()
    camera.type = mj.mjtCamera.mjCAMERA_FREE
    camera.lookat = [2.5, 0, 0]
    camera.distance = 10
    camera.azimuth = 0
    camera.elevation = -90

    # Initialize world to get the background
    mj.set_mjcb_control(None)
    world = OlympicArena()
    model = world.spec.compile()
    data = mj.MjData(model)
    save_path = str(DATA / "background.png")
    single_frame_renderer(
        model,
        data,
        camera=camera,
        save_path=save_path,
        save=True,
    )

    # Setup background image
    img = plt.imread(save_path)
    _, ax = plt.subplots()
    ax.imshow(img)
    w, h, _ = img.shape

    # Convert list of [x,y,z] positions to numpy array
    pos_data = np.array(history)

    # Calculate initial position
    x0, y0 = int(h * 0.483), int(w * 0.815)
    xc, yc = int(h * 0.483), int(w * 0.9205)
    ym0, ymc = 0, SPAWN_POS[0]

    # Convert position data to pixel coordinates
    pixel_to_dist = -((ymc - ym0) / (yc - y0))
    pos_data_pixel = [[xc, yc]]
    for i in range(len(pos_data) - 1):
        xi, yi, _ = pos_data[i]
        xj, yj, _ = pos_data[i + 1]
        xd, yd = (xj - xi) / pixel_to_dist, (yj - yi) / pixel_to_dist
        xn, yn = pos_data_pixel[i]
        pos_data_pixel.append([xn + int(xd), yn + int(yd)])
    pos_data_pixel = np.array(pos_data_pixel)

    # Plot x,y trajectory
    ax.plot(x0, y0, "kx", label="[0, 0, 0]")
    ax.plot(xc, yc, "go", label="Start")
    ax.plot(pos_data_pixel[:, 0], pos_data_pixel[:, 1], "b-", label="Path")
    ax.plot(pos_data_pixel[-1, 0], pos_data_pixel[-1, 1], "ro", label="End")

    # Add labels and title
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.legend()
    plt.title("Robot Path in XY Plane")
    plt.show()

    # Cleanup
    del model
    del data
    del world
    gc.collect()


def plot_evolution_progress(fitness_history, title, save_path=None):
    """Plot fitness over generations."""
    plt.figure(figsize=(10, 6))
    plt.plot(fitness_history, 'b-', label='Best Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


class CPG_controller:
    """Central Pattern Generator controller using sinusoidal oscillations."""
    
    def __init__(self, output_size, genotype=None):
        self.output_size = output_size

        # Each actuator has [amplitude, frequency, phase]
        if genotype is None:
            self.params = self._initialize_random_params()
        else:
            self.genotype_to_params(genotype)

    def _initialize_random_params(self):
        """Initialize random CPG parameters in correct order."""
        params = np.zeros((self.output_size, 3))
        for i in range(self.output_size):
            params[i, 0] = RNG.uniform(0.1, 1.0)      # Amplitude
            params[i, 1] = RNG.uniform(1.0, 4.0)      # Frequency
            params[i, 2] = RNG.uniform(0, 2 * np.pi)  # Phase
        return params

    def genotype_to_params(self, genotype):
        """Convert flat genotype to parameter matrix."""
        num_params = self.output_size * 3
        if len(genotype) < num_params:
            genotype = np.pad(genotype, (0, num_params - len(genotype)))
        self.params = np.array(genotype[:num_params]).reshape(self.output_size, 3)

    def outputs(self, model: mj.MjModel, data: mj.MjData) -> np.ndarray:
        """Generate control signals based on sinusoidal oscillations."""
        t = data.time
        ctrl = np.zeros(self.output_size)
        for i in range(self.output_size):
            A, w, phi = self.params[i]
            # Scale to reasonable actuator range
            ctrl[i] = A * np.sin(w * t + phi) * (np.pi / 2)
        return ctrl


def genotype_to_body(individual):
    """Convert body genotype to robot specification."""
    genotype = [
        np.array(individual[0:64], dtype=np.float32),
        np.array(individual[64:128], dtype=np.float32),
        np.array(individual[128:192], dtype=np.float32)
    ]

    p_matrices = NDE.forward(genotype)

    # Decode the high-probability graph
    hpd = HighProbabilityDecoder(NUM_OF_MODULES)
    robot_graph: DiGraph[Any] = hpd.probability_matrices_to_graph(
        p_matrices[0],
        p_matrices[1],
        p_matrices[2],
    )
    robot_spec = construct_mjspec_from_graph(robot_graph)
    return robot_spec, robot_graph


def body_to_size(body_individual):
    """Extract input/output sizes from body with proper cleanup."""
    mj.set_mjcb_control(None)
    
    try:
        core, _ = genotype_to_body(body_individual)
        temp_core = core.spec.to_xml()
        temp_spec = mj.MjSpec.from_string(temp_core)

        # Initialize world
        temp_world = OlympicArena()

        # Spawn robot in the world
        temp_world.spawn(temp_spec, spawn_position=SPAWN_POS, correct_for_bounding_box=False)

        # Generate the model and data
        model = temp_world.spec.compile()
        data = mj.MjData(model)

        input_size = int(len(data.qpos.copy()))
        output_size = int(len(data.ctrl.copy()))

        # Cleanup
        del data
        del model
        del temp_world
        del temp_spec
        
    finally:
        gc.collect()
        mj.set_mjcb_control(None)
    
    return input_size, output_size, core


def evaluate_brain_for_body(core, brain_individual, input_size, output_size):
    """Evaluate a CPG brain for a given body."""
    try:
        cpg_controller_instance = CPG_controller(output_size, brain_individual)
        tracker = Tracker(
            mujoco_obj_to_find=mj.mjtObj.mjOBJ_GEOM,
            name_to_bind="core"
        )
        ctrl = Controller(
            controller_callback_function=cpg_controller_instance.outputs,
            tracker=tracker,
        )

        experiment(robot=core, controller=ctrl, mode="simple", duration=SIMULATION_DURATION)
        
        # Safety check for tracker data
        if not tracker.history["xpos"] or len(tracker.history["xpos"]) == 0:
            return -1000.0  # Penalty for failed tracking
            
        fitness = fitness_function(tracker.history["xpos"][0])
        
    finally:
        # Cleanup
        del cpg_controller_instance
        del tracker
        del ctrl
        gc.collect()
    
    return fitness


def init_cpg_individual(output_size):
    """Initialize CPG genotype in correct order: [A1, w1, phi1, A2, w2, phi2, ...]."""
    genome = []
    for _ in range(output_size):
        genome.append(RNG.uniform(0.1, 1.0))      # Amplitude
        genome.append(RNG.uniform(1.0, 4.0))      # Frequency  
        genome.append(RNG.uniform(0, 2 * np.pi))  # Phase
    return genome


def setup_ea(ea_type, body_individual=None):
    """Setup evolutionary algorithm toolbox for brain or body evolution."""
    toolbox = base.Toolbox()
    
    if ea_type == "brain":
        input_size, output_size, core = body_to_size(body_individual)
        brain_genome_length = output_size * 3
        print(f"[setup_ea] CPG Controller - Output size = {output_size}, Genome length = {brain_genome_length}")
        
        toolbox.register("individual", lambda: creator.BrainIndividual(init_cpg_individual(output_size)))
        
        def brain_evaluator(brain_individual):
            fitness = evaluate_brain_for_body(core, brain_individual, input_size, output_size)
            return (fitness,)
        
        toolbox.register("evaluate", brain_evaluator)

    elif ea_type == "body":
        toolbox.register("attr_float", RNG.random)
        toolbox.register(
            "individual",
            tools.initRepeat,
            creator.BodyIndividual,
            toolbox.attr_float,
            n=BODY_GENOME_LENGTH,
        )

        def body_evaluator(body_individual):
            print(f"[body_evaluator] Evaluating body individual...")

            try:
                # Build the body
                input_size, output_size, core = body_to_size(body_individual)

                # Skip invalid bodies (no actuators)
                if output_size == 0:
                    print("Skipping body with no actuators.")
                    return (-500.0,)

                # QUICK test brain (no evolution here)
                test_brain = init_cpg_individual(output_size)
                fitness = evaluate_brain_for_body(core, test_brain, input_size, output_size)

                # Store best brain (so final run can evolve it fully)
                body_individual.best_brain = test_brain

                return (fitness,)

            except Exception as e:
                print(f"[body_evaluator] Error: {e}")
                return (-1000.0,)  # Penalty for failed body

        toolbox.register("evaluate", body_evaluator)

    # Standard DEAP operators for both types
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.05, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # make sure this stays at the END
    return toolbox




def run_ea_generation(toolbox, ngen, cxpb, mutpb, k, pop_size, ea_type):
    """Run evolutionary algorithm for specified generations."""
    population = toolbox.population(n=pop_size)
    best_fitness_history = []

    # Mutation parameter control
    sigma_start = 0.5
    sigma_end = 0.1
    indpb_start = 0.4
    indpb_end = 0.1

    for gen in range(ngen):
        print(f"\n{'='*60}")
        print(f"{ea_type.upper()} Generation {gen}/{ngen-1}")
        print(f"{'='*60}")
        
        # Linear annealing for mutation parameters
        progress = gen / max(ngen - 1, 1)
        sigma = sigma_start * (1 - progress) + sigma_end * progress
        indpb = indpb_start * (1 - progress) + indpb_end * progress

        # Evaluate all individuals with invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        print(f"Evaluating {len(invalid_ind)} new individuals...")
        
        for idx, ind in enumerate(invalid_ind):
            print(f"  Evaluating individual {idx+1}/{len(invalid_ind)}...")
            ind.fitness.values = toolbox.evaluate(ind)
            
            # Periodic cleanup
            if idx % 5 == 0:
                gc.collect()

        # Select parents (tournament selection)
        offspring = toolbox.select(population, len(population) - k)
        offspring = list(map(toolbox.clone, offspring))

        # Crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Mutation with annealed parameters
        for mutant in offspring:
            if random.random() < mutpb: 
                tools.mutGaussian(mutant, mu=0, sigma=sigma, indpb=indpb)
                del mutant.fitness.values

        # Re-evaluate modified offspring
        invalid_off = [ind for ind in offspring if not ind.fitness.valid]
        print(f"Re-evaluating {len(invalid_off)} modified offspring...")
        
        for idx, ind in enumerate(invalid_off):
            print(f"  Re-evaluating offspring {idx+1}/{len(invalid_off)}...")
            ind.fitness.values = toolbox.evaluate(ind)
            if idx % 5 == 0:
                gc.collect()

        # Add elites from previous population
        elites = tools.selBest(population, k)
        offspring.extend(list(map(toolbox.clone, elites)))

        # Replace population
        population[:] = offspring

        # Track and print best fitness
        best = tools.selBest(population, 1)[0]
        best_fitness_history.append(best.fitness.values[0])
        print(f"\n{ea_type.upper()} Gen {gen} COMPLETE | Best fitness: {best.fitness.values[0]:.3f} | sigma={sigma:.3f} | indpb={indpb:.3f}")
        
        # Force cleanup after each generation
        gc.collect()
        
    return population, best_fitness_history, best


def evolve_brain_for_body(body_individual):
    """Evolve a CPG controller for a given body."""
    print(f"\n{'*'*60}")
    print("Starting BRAIN evolution for current body")
    print(f"{'*'*60}")

    toolbox = None
    brain_population = []
    best_brain = None

    try:
        toolbox = setup_ea("brain", body_individual)
        brain_population, best_fit_hist, best_brain = run_ea_generation(
            toolbox,
            ngen=BRAIN_GENERATIONS,
            cxpb=BRAIN_CROSSOVER_PROBABILITY,
            mutpb=BRAIN_MUTATION_PROBABILITY,
            k=BRAIN_NUMBER_OF_ELITES,
            pop_size=BRAIN_POPULATION_SIZE,
            ea_type="brain"
        )
        print(f"{'*'*60}")
        print(f"BRAIN evolution complete | Best fitness: {best_brain.fitness.values[0]:.3f}")
        print(f"{'*'*60}\n")

    except Exception as e:
        print(f"[evolve_brain_for_body] Exception: {e}")
        # Return a dummy brain to keep EA running
        best_brain = creator.BrainIndividual([])
        best_brain.fitness.values = (-1000.0,)

    finally:
        del toolbox
        del brain_population
        gc.collect()

    return best_brain


def nested_evolution():
    """Run nested evolution: evolve bodies, each with evolved brain."""
    print("\n" + "="*80)
    print("STARTING NESTED EVOLUTION")
    print("="*80 + "\n")
    
    toolbox = setup_ea("body")
    body_population, best_fit_hist, best_individual = run_ea_generation(
        toolbox,
        ngen=BODY_GENERATIONS, 
        cxpb=BODY_CROSSOVER_PROBABILITY,
        mutpb=BODY_MUTATION_PROBABILITY,
        k=BODY_NUMBER_OF_ELITES,
        pop_size=BODY_POPULATION_SIZE,
        ea_type="body"
    )    
    
    print("\n" + "="*80)
    print("NESTED EVOLUTION COMPLETE")
    print("="*80 + "\n")
    
    return {
        'best_individual': best_individual,
        'fitness_history': best_fit_hist,
        'final_population': body_population,
        'best_fitness': best_fit_hist[-1] if best_fit_hist else None
    }


def run_best_individual(best_individual, pre_constructed_body=None, mode: ViewerTypes = "launcher"):
    """Run the best individual with its evolved CPG controller."""
    if best_individual.best_brain is None:
        console.log("Evolving brain for the final body")
        best_individual.best_brain = evolve_brain_for_body(best_individual)
    
    # Get body info
    input_size, output_size, core = body_to_size(best_individual)
    
    # Create the CPG controller
    best_cpg_controller_instance = CPG_controller(output_size, best_individual.best_brain)
    tracker = Tracker(
        mujoco_obj_to_find=mj.mjtObj.mjOBJ_GEOM,
        name_to_bind="core"
    )
    ctrl = Controller(
        controller_callback_function=best_cpg_controller_instance.outputs,
        tracker=tracker,
    )

    # Run the simulation
    experiment(robot=core, controller=ctrl, mode=mode, duration=SIMULATION_DURATION)

    # Safety check: if tracker failed to record
    if not tracker.history["xpos"] or len(tracker.history["xpos"]) == 0:
        print("Warning: No tracking data collected — tracker may not be bound correctly.")
        return [[0, 0, 0]]  # Return dummy data to prevent crash

    return tracker.history["xpos"][0]


def experiment(
    robot: Any,
    controller: Controller,
    duration: int = 15,
    mode: ViewerTypes = "launcher",
) -> None:
    """Run the simulation with specified visualization mode."""
    mj.set_mjcb_control(None)
    
    try:
        temp_core = robot.spec.to_xml()
        temp_spec = mj.MjSpec.from_string(temp_core)

        # Initialize world
        world = OlympicArena()

        # Spawn robot in the world
        world.spawn(temp_spec, spawn_position=SPAWN_POS.copy(), correct_for_bounding_box=False)

        # Generate the model and data
        model = world.spec.compile()
        data = mj.MjData(model)

        # Reset simulation state
        mj.mj_resetData(model, data)

        # Setup tracker
        if controller.tracker is not None:
            controller.tracker.setup(world.spec, data)
            print(f"Tracker setup complete. Tracking object: {controller.tracker.name_to_bind}")

        # Set control callback
        mj.set_mjcb_control(lambda m, d: controller.set_control(m, d))

        # Visualization mode handling
        match mode:
            case "simple":
                print("Running in SIMPLE mode (no visualization).")
                simple_runner(model, data, duration=duration)

            case "frame":
                print("Rendering single frame.")
                save_path = str(DATA / "robot.png")
                single_frame_renderer(model, data, save=True, save_path=save_path)

            case "video":
                print("Recording video of simulation...")
                path_to_video_folder = str(Path.home() / "Desktop" / "overnight_simulation_videos")
                Path(path_to_video_folder).mkdir(exist_ok=True)

                video_recorder = VideoRecorder(output_folder=path_to_video_folder)
                video_renderer(model, data, duration=duration, video_recorder=video_recorder)
                print(f"Video saved to: {path_to_video_folder}")

            case "launcher":
                print("Launching live MuJoCo viewer...")
                viewer.launch(model=model, data=data)
                input("Press ENTER to close the simulation window...")

            case "no_control":
                print("Running with manual control (no controller).")
                mj.set_mjcb_control(None)
                viewer.launch(model=model, data=data)
                input("Press ENTER to close the simulation window...")

    finally:
        # Cleanup resources
        try:
            del data
            del model
            del world
            del temp_spec
        except:
            pass
        gc.collect()
        mj.set_mjcb_control(None)


def main() -> None:
    """Entry point for nested evolution."""
    results = nested_evolution()
    best_individual = results['best_individual']
    fitness_history = results['fitness_history']

    plot_evolution_progress(
        fitness_history,
        title="Body Evolution Progress",
        save_path=str(DATA / "body_evolution_fitness.png")
    )

    core, best_robot_graph = genotype_to_body(best_individual)

    save_graph_as_json(
        best_robot_graph,
        DATA / "robot_graph.json",
    )

    # Final test run
    print("\nRunning best evolved individual...")
    history = run_best_individual(
        best_individual,
        pre_constructed_body=core,
        mode="launcher"
    )

    # Visualize trajectory
    if history and len(history) > 1:
        show_xpos_history(history)
        fitness = fitness_function(history)
        
        # Calculate and display performance metrics
        pos_array = np.array(history)
        forward_distance = pos_array[-1, 0] - pos_array[0, 0]
        total_path_length = np.sum([np.linalg.norm(pos_array[i] - pos_array[i-1]) 
                                     for i in range(1, len(pos_array))])
        
        msg = f"""
        ========================================
        FINAL ROBOT PERFORMANCE
        ========================================
        Fitness Score:       {fitness:.3f}
        Forward Distance:    {forward_distance:.3f} meters
        Total Path Length:   {total_path_length:.3f} meters
        Simulation Duration: {SIMULATION_DURATION} seconds
        Average Speed:       {total_path_length/SIMULATION_DURATION:.3f} m/s
        ========================================
        """
        console.log(msg)
    else:
        console.log("No motion data recorded. The robot may have been unstable or stationary.")


if __name__ == "__main__":
    main()