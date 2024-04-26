document.addEventListener('DOMContentLoaded', function() {
    var instance = jsPlumb.getInstance({
        DragOptions: { cursor: 'pointer', zIndex: 2000 },
        PaintStyle: { stroke: '#666' },
        EndpointStyle: { width: 20, height: 16, stroke: '#666' },
        Endpoint: ["Rectangle", { width: 20, height: 16 }],
        Anchors: ["TopCenter", "BottomCenter"],
        Container: "room-container"
    });

    const roomContainer = document.getElementById('room-container');
    roomContainer.innerHTML = '';
    const containerWidth = roomContainer.offsetWidth;
    const containerHeight = roomContainer.offsetHeight;
    let existingConnections = new Set();

    function setupRoom(room) {
        const roomDiv = document.createElement('div');
        roomDiv.className = 'room';
        roomDiv.id = 'room-' + room.room_id;
        roomDiv.style.position = 'absolute';
        roomDiv.style.padding = '10px';
        roomDiv.style.border = '1px solid black';
        roomDiv.style.width = '120px'; // Room width
        roomDiv.style.height = '100px'; // Room height
        roomDiv.style.display = 'flex';
        roomDiv.style.justifyContent = 'center';
        roomDiv.style.alignItems = 'center';
        roomDiv.innerHTML = `
            <span style="position: relative; z-index: 1;">${room.name}</span>
            <div class="controls" style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; display: flex; align-items: center; justify-content: space-between;">
                <div class="connect" style="width: 10px; height: 10px; background-color: red;"></div>
                <div class="connect" style="width: 10px; height: 10px; background-color: red;"></div>
                <div class="connect" style="width: 10px; height: 10px; background-color: red;"></div>
                <div class="connect" style="width: 10px; height: 10px; background-color: red;"></div>
                <button class="delete-room" style="position: absolute; top: 5px; right: 5px; background: none; border: none; color: red; cursor: pointer;">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>`;
    
        // Adjusting connect div positions for each side of the room
        const connects = roomDiv.querySelectorAll('.connect');
        connects.forEach(connect => {
            connect.style.backgroundColor = 'black';
            connect.style.borderRadius = '50%';
        });
        connects[0].style.transform = 'translateX(-50%)';
        connects[1].style.transform = 'translateX(775%)';
        connects[2].style.transform = 'translateY(495%) translateX(-160%)';
        connects[3].style.transform = 'translateY(-495%) translateX(-540%)';
    
        // Random positioning
        const xPosition = room.position_x !== 0.0 ? room.position_x : Math.floor(Math.random() * (containerWidth - roomDiv.offsetWidth));
        const yPosition = room.position_y !== 0.0 ? room.position_y : Math.floor(Math.random() * (containerHeight - roomDiv.offsetHeight));
        roomDiv.style.left = xPosition + 'px';
        roomDiv.style.top = yPosition + 'px';    
    
        roomContainer.appendChild(roomDiv);
    
        instance.makeSource(roomDiv, {
            filter: '.connect',
            anchor: 'Continuous',
            connectorStyle: { stroke: '#5c96bc', strokeWidth: 2, outlineStroke: 'transparent', outlineWidth: 4 },
            connectionType: "basic",
            maxConnections: 2,
            onMaxConnections: function (info, e) {
                alert("Maximum connections (" + info.maxConnections + ") reached");
            }
        });
    
        instance.makeTarget(roomDiv, {
            dropOptions: { hoverClass: 'dragHover' },
            anchor: 'Continuous'
        });
    
        instance.draggable(roomDiv, {
            grid: [20, 20],
            stop: function(params) {
                // Get the final position of the room
                var finalX = params.pos[0];
                var finalY = params.pos[1];
                // Update the database with the new position
                fetch('/profile/update_room_position/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: new URLSearchParams({
                        'room_id': room.room_id,
                        'position_x': finalX,
                        'position_y': finalY
                    }).toString()
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status !== 'success') {
                        console.error('Error updating room position:', data.message);
                        // Optionally handle the error on the client side
                    }
                })
                .catch(error => {
                    console.error('Error updating room position:', error);
                });
            }
        });
    
        document.querySelector('#room-' + room.room_id + ' .delete-room').addEventListener('click', function() {
            fetch('/profile/delete_room/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRFToken()
                },
                body: new URLSearchParams({'room_id': room.room_id}).toString()
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    instance.remove(roomDiv); // Remove the room element and its connections
                } else {
                    alert(data.message); // Show error message
                }
            })
            .catch(error => {
                console.error('Error deleting room:', error);
            });
        });
    
        return roomDiv;
    }

    instance.batch(function () {
        // Setup all rooms first
        rooms.forEach(setupRoom);

        // Then connect them
        roomConnections.forEach(connection => {
            const connectionKey = connection.source + "-" + connection.target;
            const reverseConnectionKey = connection.target + "-" + connection.source;

            // Only connect if this connection hasn't been made in either direction
            if (!existingConnections.has(connectionKey) && !existingConnections.has(reverseConnectionKey)) {
                console.log('Connecting:', 'room-' + connection.source, 'to', 'room-' + connection.target);
                instance.connect({
                    source: 'room-' + connection.source,
                    target: 'room-' + connection.target,
                });
                existingConnections.add(connectionKey);
            }
        });
    });

    document.getElementById('add-room-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var roomName = document.getElementById('room-name-input').value;

        fetch('/profile/add_room/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken()
            },
            body: new URLSearchParams({'room_name': roomName}).toString()
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                var newRoom = {room_id: data.room_id, name: data.room_name};
                setupRoom(newRoom); // Add the new room dynamically
                document.getElementById('room-name-input').value = ''; // Clear input
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error adding room:', error);
        });
    });

    instance.bind('connection', function(info) {
        const connection = info.connection;
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

    function getCSRFToken() {
        return document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
    }
});
