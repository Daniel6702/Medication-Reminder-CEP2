document.addEventListener('DOMContentLoaded', function() {
    const notifications = document.querySelectorAll('.notification-item');
    const meds = document.querySelectorAll('.medication-event');
    var events = document.querySelectorAll('.medication-event');

    notifications.forEach(notification => {
        notification.addEventListener('click', function() {
            this.style.opacity = '0';
            setTimeout(() => {
                this.remove();
            }, 500);
        });
    });

    meds.forEach(med => {
        med.addEventListener('click', function() {
            alert(`Dosage: ${this.querySelector('.medication-dosage').textContent}`);
        });
    });

    events.forEach(function(event) {
        var top = event.getAttribute('data-top') + 'px';
        var height = event.getAttribute('data-height') + 'px';

        event.style.top = top;
        event.style.height = height;
    });
});

function formatDate(isoDateString) {
    const date = new Date(isoDateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);  // Adjust 'en-US' as needed for localization
}

let currentPage = 1; // Ensure this is globally accessible and correctly updated

function changePage(direction) {
    currentPage += direction;
    loadNotifications(currentPage);
}

function loadNotifications(page) {
    console.log(`Loading page ${page}`); // Debug: Log which page is being requested
    fetch(`/profile/notifications/?page=${page}`)
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('notificationList');
            list.innerHTML = '';  // Clear current notifications

            if (data.notifications && data.notifications.length > 0) {
                data.notifications.forEach(notification => {
                    const newItem = document.createElement('li');
                    newItem.classList.add('notification-item', notification.type.toLowerCase());
                    newItem.innerHTML = `
                        <span class="notification-message">${notification.message}</span>
                        <span class="notification-timestamp">${formatDate(notification.timestamp)}</span>
                    `;
                    list.appendChild(newItem);
                });

                document.getElementById('currentPage').textContent = page;
                document.getElementById('prevPage').disabled = page === 1;  // Disable if on the first page
                document.getElementById('nextPage').disabled = !data.has_next;  // Disable if no more pages
            } else {
                document.getElementById('nextPage').disabled = true; // Disable if no data
            }
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
            currentPage -= direction; // Revert page change on error
        });
}

document.addEventListener('DOMContentLoaded', function() {
    loadNotifications(currentPage);  // Load the initial page of notifications
});
