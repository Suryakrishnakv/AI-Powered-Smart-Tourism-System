/**
 * Interactive Leaflet Map Picker for Django Admin
 * Enables visual coordinate picking, marker dragging, and verified location inspection.
 */
document.addEventListener('DOMContentLoaded', function () {
    const latInput = document.getElementById('id_latitude');
    const lngInput = document.getElementById('id_longitude');

    if (!latInput || !lngInput) return;

    // Create container for Leaflet map inside admin fieldset
    const container = document.createElement('div');
    container.id = 'admin-leaflet-picker-wrapper';
    container.style.margin = '14px 0 20px 0';
    container.style.maxWidth = '800px';

    const mapTitle = document.createElement('div');
    mapTitle.innerHTML = '<strong style="display:block; margin-bottom:6px; color:#0b6e4f;"><i class="bi bi-geo-alt"></i> Interactive GPS Coordinate Picker (Click or drag marker to set coordinates)</strong>';
    container.appendChild(mapTitle);

    const mapDiv = document.createElement('div');
    mapDiv.id = 'admin-leaflet-picker-map';
    mapDiv.style.height = '340px';
    mapDiv.style.width = '100%';
    mapDiv.style.borderRadius = '8px';
    mapDiv.style.border = '2px solid #0b6e4f';
    mapDiv.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
    container.appendChild(mapDiv);

    // Insert after coordinates row
    const targetParent = latInput.closest('.form-row') || latInput.parentElement;
    targetParent.parentElement.insertBefore(container, targetParent.nextSibling);

    // Initial coordinates (default to Kerala center if empty)
    let curLat = parseFloat(latInput.value) || 9.35;
    let curLng = parseFloat(lngInput.value) || 76.85;
    let hasCoords = Boolean(latInput.value && lngInput.value);

    // Initialize Leaflet Map
    if (typeof L === 'undefined') return;

    const map = L.map('admin-leaflet-picker-map').setView([curLat, curLng], hasCoords ? 13 : 8);

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles &copy; Esri &mdash; Esri, OpenStreetMap'
    }).addTo(map);

    let marker = null;
    if (hasCoords) {
        marker = L.marker([curLat, curLng], { draggable: true }).addTo(map);
        marker.bindPopup("Verified Location").openPopup();
    }

    function updateInputs(lat, lng) {
        latInput.value = lat.toFixed(6);
        lngInput.value = lng.toFixed(6);
    }

    if (marker) {
        marker.on('dragend', function (e) {
            const pos = e.target.getLatLng();
            updateInputs(pos.lat, pos.lng);
        });
    }

    map.on('click', function (e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        if (!marker) {
            marker = L.marker([lat, lng], { draggable: true }).addTo(map);
            marker.on('dragend', function (ev) {
                const p = ev.target.getLatLng();
                updateInputs(p.lat, p.lng);
            });
        } else {
            marker.setLatLng([lat, lng]);
        }
        updateInputs(lat, lng);
    });

    // Update marker if admin types numbers manually
    function onManualChange() {
        const valLat = parseFloat(latInput.value);
        const valLng = parseFloat(lngInput.value);
        if (!isNaN(valLat) && !isNaN(valLng)) {
            if (!marker) {
                marker = L.marker([valLat, valLng], { draggable: true }).addTo(map);
            } else {
                marker.setLatLng([valLat, valLng]);
            }
            map.setView([valLat, valLng], 13);
        }
    }

    latInput.addEventListener('change', onManualChange);
    lngInput.addEventListener('change', onManualChange);

    setTimeout(function () {
        map.invalidateSize();
    }, 400);
});
