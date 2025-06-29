// Updated: 2025-06-22
// By Scott O.
// Map visualization for service requests using Leaflet.js. Initializes a Leaflet map and fetches request data to display on the map.
const map = L.map('map').setView([21.3069, -157.8583], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let geoJsonLayer = null;

// Debounce utility function
function debounce(func, delay) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), delay);
  };
}

// Core search logic
function applyFilters() {
  const type = document.getElementById('searchType').value;
  const desc = document.getElementById('searchDescription').value;
  const start = document.getElementById('startDate').value;
  const end = document.getElementById('endDate').value;

  const params = new URLSearchParams({
    type,
    desc,
    start,
    end
  });

  fetch(`/api/requests?${params.toString()}`)
    .then(response => response.json())
    .then(data => {
      // Remove old layer
      if (geoJsonLayer) {
        map.removeLayer(geoJsonLayer);
      }

      // Add new filtered data
      geoJsonLayer = L.geoJSON(data, {
        onEachFeature: function (feature, layer) {
          layer.bindPopup(`
            <strong>${feature.properties.service}</strong><br>
            Status: ${feature.properties.status}<br>
            Request ID: ${feature.properties.id}<br>
            Date: ${new Date(feature.properties.requested_datetime).toLocaleDateString()}<br> 
              ${feature.properties.description}
    `);

        }
      });

      geoJsonLayer.addTo(map);
    });
}

// Debounced version of applyFilters
const debouncedFilter = debounce(applyFilters, 300);

// Attach to input events
['searchType', 'searchDescription', 'startDate', 'endDate'].forEach(id => {
  document.getElementById(id).addEventListener('input', debouncedFilter);
});

// Load full dataset on initial map load
applyFilters();

// Clear Filters button logic
document.getElementById('clearFilters').addEventListener('click', () => {
  document.getElementById('searchType').value = '';
  document.getElementById('searchDescription').value = '';
  document.getElementById('startDate').value = '';
  document.getElementById('endDate').value = '';
  applyFilters();  // Reset map to show all requests
});