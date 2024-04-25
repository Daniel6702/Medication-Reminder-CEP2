document.addEventListener('DOMContentLoaded', function() {
    var instance = jsPlumb.getInstance({
        DragOptions: { cursor: 'pointer', zIndex: 2000 },
        PaintStyle: { stroke: '#666' },
        EndpointStyle: { width: 20, height: 16, stroke: '#666' },
        Endpoint: ["Rectangle", { width: 20, height: 16 }],
        Anchors: ["TopCenter", "BottomCenter"],
        Container: "room-container" // Ensure jsPlumb knows where to find the elements
    });

    const roomContainer = document.getElementById('room-container');
    const containerWidth = roomContainer.offsetWidth;
    const containerHeight = roomContainer.offsetHeight;

    console.log(data);
    var roomConnections = data;


    instance.batch(function () {
        var rooms = document.querySelectorAll('.room');
        rooms.forEach(room => {
            const xPosition = Math.floor(Math.random() * (containerWidth - room.offsetWidth));
            const yPosition = Math.floor(Math.random() * (containerHeight - room.offsetHeight));
            room.style.left = xPosition + 'px';
            room.style.top = yPosition + 'px';

            instance.makeSource(room, {
                filter: '.connect',
                anchor: 'Continuous',
                connectorStyle: { stroke: '#5c96bc', strokeWidth: 2, outlineStroke: 'transparent', outlineWidth: 4 },
                connectionType: "basic",
                maxConnections: 2,
                onMaxConnections: function (info, e) {
                    alert("Maximum connections (" + info.maxConnections + ") reached");
                }
            });

            instance.makeTarget(room, {
                dropOptions: { hoverClass: 'dragHover' },
                anchor: 'Continuous'
            });

            instance.draggable(room, {
                grid: [20, 20]
            });

            roomConnections.forEach(function(connection) {
                console.log('Connecting:', 'room-' + connection.source, 'to', 'room-' + connection.target);
                jsPlumb.connect({
                    source: 'room-' + connection.source,
                    target: 'room-' + connection.target,
                });
            });
    
        });
    });

    instance.bind('connection', function(info) {
        const connection = info.connection;
        // Assuming the id is in the format "room-<UUID>", extract the UUID part
        const sourceId = connection.sourceId.substring(connection.sourceId.indexOf('-') + 1);
        const targetId = connection.targetId.substring(connection.targetId.indexOf('-') + 1);
    
        fetch("/profile/connect_rooms/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ room1_id: sourceId, room2_id: targetId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                alert(data.message);
                instance.deleteConnection(connection);
            }
        })
        .catch(error => {
            console.error('Error connecting rooms:', error);
        });
    });

    function getCSRFToken() { // Get CSRF token from cookie
        return document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
    }
});
