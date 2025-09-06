async function uploadImage() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.onchange = async () => {
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.license_plate) {
            document.getElementById('license_plate').value = data.license_plate;
            document.getElementById('vehicle_type').value = data.vehicle_type;
        }
    };
    fileInput.click();
}

async function submitForm() {
    const license_plate = document.getElementById('license_plate').value;
    const vehicle_type = document.getElementById('vehicle_type').value;
    const additional_toll_fee = document.getElementById('additional_toll_fee').value;
    const response = await fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ license_plate, vehicle_type, additional_toll_fee })
    });
    const data = await response.json();
    if (data.success) {
        loadEntries();
    }
}

async function loadEntries() {
    const response = await fetch('/load');
    const entries = await response.json();
    const tableBody = document.getElementById('entries_table');
    tableBody.innerHTML = '';
    let totalTollFee = 0;
    entries.forEach(entry => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${entry['License Plate']}</td><td>${entry['Vehicle Type']}</td><td>${entry['Toll Fee']}</td><td>${entry['Date/Time']}</td>`;
        tableBody.appendChild(row);
        totalTollFee += parseInt(entry['Toll Fee']);
    });
    document.getElementById('total_label').innerHTML = `<div class="total">Total Toll Fee: ${totalTollFee}</div>`;
}

async function startLiveScan() {
    const imageFrame = document.getElementById('live_feed');
    imageFrame.src = '/video_feed';
    document.querySelector('.capture-button').style.display = 'block';
    document.querySelector('.close-button').style.display = 'block';
}

async function captureImage() {
    const response = await fetch('/capture', {
        method: 'POST'
    });
    const data = await response.json();
    if (data.license_plate) {
        document.getElementById('license_plate').value = data.license_plate;
        document.getElementById('vehicle_type').value = data.vehicle_type;
    }
}

function closeLiveView() {
    const imageFrame = document.getElementById('live_feed');
    imageFrame.src = '';
    document.querySelector('.capture-button').style.display = 'none';
    document.querySelector('.close-button').style.display = 'none';
}

window.onload = loadEntries;
