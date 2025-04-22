function generateTimeSlots() {
  const timeSlotSelect = document.getElementById("timeSlot");
  const startHour = 9; // 9 AM
  const endHour = 20; // 8 PM

  for (let hour = startHour; hour < endHour; hour++) {
    const startTime = `${hour}:00`;
    const endTime = `${hour + 1}:00`;
    const option = document.createElement("option");
    option.value = `${startTime}-${endTime}`;
    option.textContent = `${startTime} - ${endTime}`;
    timeSlotSelect.appendChild(option);
  }
}

document.getElementById("city").addEventListener("change", async function () {
  console.log("this.value", this.value);
  const selectedCity = this.value == "Delhi" ? "new-delhi" : this.value;

  if (selectedCity) {
    console.log("City selected:", selectedCity);
    try {
      // 🔁 Replace this URL with your actual API endpoint
      const response = await fetch(
        `http://localhost:5150/api/localities?city=${selectedCity}`
      );

      if (!response.ok) throw new Error("API call failed");

      const data = await response.json();
      // console.log("API response:", data);
      const localitiesGroup = document.getElementById("localitiesGroup");

      // Remove all existing checkboxes except "Select All"
      localitiesGroup
        .querySelectorAll(".checkbox-item:not(.select-all-item)")
        .forEach((el) => el.remove());

      // Append checkboxes
      data.data.popularLocations.forEach((location) => {
        // console.log(location.googlePlaceId);
        const checkboxItem = document.createElement("div");
        checkboxItem.className = "checkbox-item";

        checkboxItem.innerHTML = `
            <div class="checkbox-item">
                <label>
                    <input type="checkbox" name="localities" value="${location.googlePlaceId}">
                    ${location.name}
                </label>
            </div>
    `;

        localitiesGroup.appendChild(checkboxItem);
        setupSelectAll("localitiesGroup", "selectAllLocalities");
      });
    } catch (error) {
      console.error("Error fetching data for selected city:", error);
    }
  }
});

// Update price range value display
// function updatePriceValue() {
//   const priceRange = document.getElementById("priceRange");
//   const priceValue = document.getElementById("priceValue");
//   // priceValue.textContent = `₹${priceRange.value}`;
// }

function setupPriceRangeSlider() {
  const minSlider = document.getElementById("priceMin");
  const maxSlider = document.getElementById("priceMax");
  const minDisplay = document.getElementById("minValue");
  const maxDisplay = document.getElementById("maxValue");
  const rangeTrack = document.querySelector(".slider-track::before");

  function updateValues() {
    let minVal = parseInt(minSlider.value);
    let maxVal = parseInt(maxSlider.value);

    if (minVal > maxVal) {
      if (this === minSlider) {
        minVal = maxVal;
        minSlider.value = maxVal;
      } else {
        maxVal = minVal;
        maxSlider.value = minVal;
      }
    }

    minDisplay.textContent = minVal.toLocaleString();
    maxDisplay.textContent = maxVal.toLocaleString();

    // Update the visual range track
    const minPercentage =
      ((minVal - parseInt(minSlider.min)) /
        (parseInt(minSlider.max) - parseInt(minSlider.min))) *
      100;
    const maxPercentage =
      ((maxVal - parseInt(maxSlider.min)) /
        (parseInt(maxSlider.max) - parseInt(maxSlider.min))) *
      100;

    rangeTrack.style.left = `${minPercentage}%`;
    rangeTrack.style.right = `${100 - maxPercentage}%`;
  }

  minSlider.addEventListener("input", updateValues);
  maxSlider.addEventListener("input", updateValues);

  // Initial update
  updateValues();
}

// Call this function when the DOM is loaded
// document.addEventListener("DOMContentLoaded", setupPriceRangeSlider);

// Email validation
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Handle select all functionality
function setupSelectAll(groupId, selectAllId) {
  const group = document.getElementById(groupId);
  const selectAllCheckbox = document.getElementById(selectAllId);
  const checkboxes = group.querySelectorAll(
    'input[type="checkbox"]:not(#' + selectAllId + ")"
  );
  // When individual checkboxes change, update the "Select All" checkbox
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const allChecked = Array.from(checkboxes).every((cb) => cb.checked);
      selectAllCheckbox.checked = allChecked;
    });
  });

  // When "Select All" checkbox changes, update all individual checkboxes
  selectAllCheckbox.addEventListener("change", function () {
    checkboxes.forEach((checkbox) => {
      checkbox.checked = this.checked;
    });
  });
}

// Form submission
document.getElementById("bookingForm").addEventListener("submit", function (e) {
  e.preventDefault();

  // Get all form values
  const product = document.getElementById("product").value;
  const city =
    document.getElementById("city").value.toLowerCase() == "delhi"
      ? "new-delhi"
      : document.getElementById("city").value.toLowerCase();
  // const localities = document.getElementById('localities').value;
  const capacity = parseInt(document.getElementById("capacity").value);
  const date = document.getElementById("date").value;
  const duration = parseInt(document.getElementById("duration").value);
  const timeSlot = document.getElementById("timeSlot").value;
  const sortBy = document.getElementById("sortBy").value;
  // const priceRange = document.getElementById("priceRange").value;
  const receiverEmail = document.getElementById("receiverEmail").value;
  const name = document.getElementById("name").value;
  const priceMin = document.getElementById("priceMin").value;
  const priceMax = document.getElementById("priceMax").value;


  // Get selected brands
  const selectedLocalities = Array.from(
    document.querySelectorAll('input[name="localities"]:checked')
  ).map((checkbox) => checkbox.value);
  const selectedBrands = Array.from(
    document.querySelectorAll('input[name="brands"]:checked')
  ).map((checkbox) => checkbox.value);

  // Get selected equipments
  const selectedEquipments = Array.from(
    document.querySelectorAll('input[name="equipments"]:checked')
  ).map((checkbox) => checkbox.value);

  // Get selected amenities
  const selectedAmenities = Array.from(
    document.querySelectorAll('input[name="amenities"]:checked')
  ).map((checkbox) => checkbox.value);
  // Create the API request payload
  const payload = {
    receiverEmail: receiverEmail,
    name: name,
    request: {
      url: `/${city}/meeting-room/${city}`,
      selectedFilters: {
        PRODUCT: product === "meeting_room" ? "MEETING_ROOM" : "DAY_PASS",
        CITY: city,
        LOCALITIES: selectedLocalities, // You might want to handle multiple localities
        CAPACITY: capacity,
        DATE_DURATION_TIME: {
          DURATION: duration,
          BOOKING_DATE: new Date(date).toISOString(),
          TIME_SLOT: [],
        },
        SORT_BY: sortBy,
        EQUIPMENTS: [],
        BRANDS: selectedBrands,
        PRICE_RANGE: {
          range: [parseInt(priceMin), parseInt(priceMax)],
        },
        AMENITIES: [],
      },
      pageNo: 1,
      pageLimit: 16,
    },
  };

  console.log("payload", payload);

  fetch("http://127.0.0.1:5000/run-model", {
    // Replace with your Flask API endpoint
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json()) // Parsing the JSON response
    .then((responseData) => {
      // Handling success response
      alert("Form submitted successfully!");
      console.log(responseData);
    })
    .catch((error) => {
      // Handling error response
      alert("There was an error submitting the form. Please try again later.");
      console.error("Error:", error);
    });

  // For development testing, just log the payload
  // Send payload to external API
  // Send payload to your own backend API
  fetch("http://localhost:5150/api/book", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload["request"]),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("API Response:", data);

      // Success message
      const button = document.querySelector('button[type="submit"]');
      button.innerHTML = '<i class="fas fa-check"></i> Submitted Successfully!';
      button.style.backgroundColor = "var(--success-color)";

      setTimeout(() => {
        document.getElementById("bookingForm").reset();
        button.innerHTML = "Submit";
        button.style.backgroundColor = "var(--primary-color)";
      }, 1500);
    })
    .catch((error) => {
      console.error("API call failed:", error);
      alert("Something went wrong. Please try again.");
    });

  // Show success message without making the actual API call
  const button = document.querySelector('button[type="submit"]');
  button.innerHTML = '<i class="fas fa-check"></i> Submitted Successfully!';
  button.style.backgroundColor = "var(--success-color)";

  setTimeout(() => {
    document.getElementById("bookingForm").reset();
    button.innerHTML = "Submit";
    button.style.backgroundColor = "var(--primary-color)";
  }, 1500);
});

// Initialize the form
document.addEventListener("DOMContentLoaded", function () {
  // generateTimeSlots();
  // updatePriceValue();

  // Add event listener for price range
  // document
  //   .getElementById("priceRange")
    // .addEventListener("input", updatePriceValue);

  // Setup select all functionality
  setupSelectAll("brandsGroup", "selectAllBrands");
  setupSelectAll("equipmentsGroup", "selectAllEquipments");
  setupSelectAll("amenitiesGroup", "selectAllAmenities");

  // Initialize Flatpickr date picker
  flatpickr("#date", {
    dateFormat: "Y-m-d",
    minDate: "today",
    maxDate: new Date().fp_incr(60), // Allow booking up to 30 days in advance
    disable: [
      // function (date) {
      //   // Disable weekends
      //   return date.getDay() === 0 || date.getDay() === 6;
      // },
    ],
    locale: {
      firstDayOfWeek: 1, // Start week on Monday
    },
    onChange: function (selectedDates, dateStr, instance) {
      // Add animation when date is selected
      const input = document.getElementById("date");
      input.style.animation = "none";
      input.offsetHeight; // Trigger reflow
      input.style.animation = "pulse 0.5s";
    },
  });

  // Add pulse animation for date selection
  const style = document.createElement("style");
  style.innerHTML = `
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(74, 108, 247, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(74, 108, 247, 0); }
            100% { box-shadow: 0 0 0 0 rgba(74, 108, 247, 0); }
        }
    `;
  document.head.appendChild(style);
  setupPriceRangeSlider()
});

// function setupPriceRangeSlider() {
//   const minSlider = document.getElementById("priceMin");
//   const maxSlider = document.getElementById("priceMax");
//   const minDisplay = document.getElementById("minValue");
//   const maxDisplay = document.getElementById("maxValue");

//   function updateValues() {
//     let minVal = parseInt(minSlider.value);
//     let maxVal = parseInt(maxSlider.value);

//     // Ensure min doesn't exceed max
//     if (minVal > maxVal) {
//       if (this === minSlider) {
//         minVal = maxVal;
//         minSlider.value = maxVal;
//       } else {
//         maxVal = minVal;
//         maxSlider.value = minVal;
//       }
//     }

//     // Update display values
//     minDisplay.textContent = minVal.toLocaleString();
//     maxDisplay.textContent = maxVal.toLocaleString();
//   }

//   minSlider.addEventListener("input", updateValues);
//   maxSlider.addEventListener("input", updateValues);

//   // Initial update
//   updateValues();
// }
