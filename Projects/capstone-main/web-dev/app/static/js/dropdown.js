document.addEventListener('DOMContentLoaded', function () {
  const checkboxes = document.querySelectorAll('.country_dropdown input[type="checkbox"]');
  const tagsContainer = document.querySelector('.selected-tags');
  const searchInput = document.getElementById('countrySearch');
  const countryLabels = document.querySelectorAll('.country_dropdown label');
  const dropdown = document.getElementById('countryDropdown');
  const dropdownWrapper = document.getElementById('dropdownWrapper');

  // Assing unique ID to label and checkbox
  checkboxes.forEach((checkbox, index) => {
    const idVal = 'country_' + index;
    checkbox.id = idVal;
    const label = checkbox.nextElementSibling;
    label.setAttribute('for', idVal);
  });

  // Limit checbox selection to 2 countries
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function (e) {
      const selected = document.querySelectorAll('.country_dropdown input[type="checkbox"]:checked');
      if (selected.length > 2) {
        e.preventDefault();
        this.checked = false;
        return;
      }

      if (this.checked) {
        const tag = document.createElement('div');
        tag.classList.add('tag');
        tag.setAttribute('data-country', this.value);
        tag.innerHTML = `
          <span>${this.value}</span>
          <div class="remove-tag" onclick="removeTag(this)">&#10005;</div>
        `;
        tagsContainer.appendChild(tag);
      } else {
        const existingTag = tagsContainer.querySelector(`.tag[data-country="${this.value}"]`);
        if (existingTag) {
          tagsContainer.removeChild(existingTag);
        }
      }
    });
  });

  // Allow to remove country tags
  window.removeTag = function (button) {
    const tag = button.closest('.tag');
    const countryName = tag.getAttribute('data-country');
    const checkbox = document.querySelector(`input[type="checkbox"][value="${countryName}"]`);
    if (checkbox) {
      checkbox.checked = false;
    }
    tag.remove();
  };

  // Ensure search input exists before event listeners
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const query = this.value.toLowerCase();
      countryLabels.forEach(label => {
        const countryName = label.textContent.toLowerCase();
        label.closest('.checkbox-item').style.display = countryName.includes(query) ? 'flex' : 'none';
      });
    });

    // Open dropdown when clicking on search bar
    searchInput.addEventListener('focus', function () {
      dropdown.classList.add('open');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function (e) {
      if (!dropdownWrapper.contains(e.target)) {
        dropdown.classList.remove('open');
      }
    });

  } else {
    console.log('No search input');
  }
});
