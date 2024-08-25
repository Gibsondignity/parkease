// Firebase configuration
var firebaseConfig = {
    apiKey: "AIzaSyCfryOB57bf-oSSiZ3NUzTKLA7cvsuslJU",
    authDomain: "http://parkease808802.firebaseapp.com",
    databaseURL: "https://parkease808802-default-rtdb.firebaseio.com",
    projectId: "parkease808802",
    storageBucket: "http://parkease808802.appspot.com/",
    messagingSenderId: "438355709019",
    appId: "1:438355709019:web:099fb339bf16a05e21c37e"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
var database = firebase.database();

// Function to update parking spots based on real-time database
function updateSpots() {
    var spots = document.querySelectorAll('.spot');
    var firstAvailableSpot = null;

    spots.forEach(spot => {
        var spotId = spot.id;
        var spotRef = database.ref('parkingSpots/' + spotId);

        spotRef.on('value', function(snapshot) {
            if (snapshot.exists() && snapshot.val().occupied) {
                spot.innerHTML = `<img src="/images/Car 5.png" alt="Car" class="car-icon"><span>${spotId}</span>`;
                spot.classList.remove('available');
                spot.classList.remove('selected');
            } else {
                spot.innerHTML = `<span>${spotId}</span><p>Available</p>`;
                spot.classList.add('available');
                spot.classList.remove('selected');

                // Set the first available spot
                if (!firstAvailableSpot) {
                    firstAvailableSpot = spot;
                }
            }

            // Automatically select the first available spot, or keep A-13 selected if it's available
            if (firstAvailableSpot && firstAvailableSpot.id === 'A-13') {
                selectSpot(firstAvailableSpot);
            } else if (firstAvailableSpot) {
                selectSpot(firstAvailableSpot);
            }
        });
    });
}

// Function to select a spot
function selectSpot(spot) {
    document.querySelectorAll('.spot').forEach(s => s.classList.remove('selected'));
    spot.classList.add('selected');
    spot.querySelector('p').textContent = "Selected";
    spot.classList.remove('available');
}

// Handle spot selection manually by clicking
document.querySelectorAll('.spot').forEach(spot => {
    spot.addEventListener('click', function() {
        selectSpot(spot);
    });
});

// Call updateSpots on page load
updateSpots();
