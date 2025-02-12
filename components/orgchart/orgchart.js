$(document).ready(function () {
    var data = JSON.parse(document.getElementById('orgchart-data').textContent);

    console.log(data);

        if ($('#orgchart-container').length) {  // Ensure the container exists
            $('#orgchart-container').orgchart({
                'data': data
    /*
                {
                    'id': '1',
                    'name': 'CEO',
                    'children': [
                        { 'id': '2', 'name': 'Manager 1' },
                        { 'id': '3', 'name': 'Manager 2' }
                    ]
                },
                'nodeContent': 'name'
                //'nodeContent': 'name'
    */
            });
        } else {
            console.error("Error: #orgchart-container does not exist.");
        }
});
