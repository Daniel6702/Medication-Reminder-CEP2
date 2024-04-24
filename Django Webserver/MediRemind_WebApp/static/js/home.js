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