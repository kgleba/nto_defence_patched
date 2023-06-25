$('#fetch-elements-button').click(function () {
    $.get('/elements', function (data) {
        if (data) {
            // Clear existing elements table
            $('#elements-table').empty();
            // Recursively build elements table
            buildElementsTable(data['elements'], $('#elements-table'), '');
        }
    });
});

function encodePath(path) {
    return path.replaceAll(',', '--').replaceAll('(', '__').replaceAll(')', '-');
}

function decodePath(path) {
    return path.replaceAll('--', ',').replaceAll('__', '(').replaceAll('-', ')');
}

function showImage(image) {
    // Define the base64-encoded image string
    var base64ImageString = `data:image/png;base64,${image}`;

    // Create a new <div> element to hold the image and close button
    var floatingImageDiv = document.createElement("div");
    floatingImageDiv.style.position = "fixed";
    floatingImageDiv.style.top = "50%";
    floatingImageDiv.style.left = "50%";
    floatingImageDiv.style.transform = "translate(-50%, -50%)";
    floatingImageDiv.style.backgroundColor = "#fff";
    floatingImageDiv.style.padding = "20px";
    floatingImageDiv.style.border = "1px solid #ccc";
    floatingImageDiv.style.boxShadow = "0 0 10px rgba(0, 0, 0, 0.5)";
    document.body.appendChild(floatingImageDiv);

    // Create a new <img> element with the base64-encoded image as its source
    var floatingImage = document.createElement("img");
    floatingImage.src = base64ImageString;
    floatingImage.style.maxWidth = "100%";
    floatingImageDiv.appendChild(floatingImage);

    // Create a new <button> element to close the floating window
    var closeButton = document.createElement("button");
    closeButton.textContent = "Close";
    closeButton.style.marginTop = "10px";
    closeButton.style.padding = "10px";
    closeButton.style.backgroundColor = "#ccc";
    closeButton.style.border = "none";
    closeButton.style.borderRadius = "5px";
    closeButton.style.cursor = "pointer";
    closeButton.addEventListener("click", function () {
        document.body.removeChild(floatingImageDiv);
    });
    floatingImageDiv.appendChild(closeButton);

}

function buildElementsTable(elements, parent, parentName) {
    for (var key in elements) {
        var path = `${parentName}.${key}`
        if (parentName == '') {
            path = key;
        }
        var section = elements[key];
        var header = $('<h5>').text(key);
        header.click(function () {
            $(this).siblings('ul').toggle();
        });
        var ul = $('<ul>').attr('element-path', path).hide();
        parent.append(header);
        parent.append(ul);

        // Create a list of functions for the section
        if (section.hasOwnProperty("methods")) {
            var methods = section.methods;
            var methodsList = $('<ul>');
            for (var i = 0; i < methods.length; i++) {
                var method = methods[i];
                var li = $('<li>');
                var method_path = encodePath(`${path}.${method}`);
                var button = $('<button>').text(`Call ${method}`).attr('path', method_path).addClass('btn btn-primary');

                // Check if method has arguments
                if (method.includes('(') && method.includes(')')) {
                    var args = method.slice(method.indexOf('(') + 1, method.indexOf(')')).split(',');
                    if (args[0]) {
                        for (var j = 0; j < args.length; j++) {
                            var argName = args[j];
                            var input_path = `${method_path}.${argName}`
                            var input = $('<input>').attr('type', 'text').attr('placeholder', argName).attr('id', input_path).addClass('form-control');
                            li.append(input);
                        }
                    }
                }

                button.click(function () {
                    // Call the method
                    var path = $(this).attr('path');
                    var path_ = decodePath(path);
                    console.log(path, path_);
                    var args_ = path_.slice(path_.indexOf('(') + 1, path_.indexOf(')')).split(',');
                    args = [];
                    if (args_[0]) {
                        for (var j = 0; j < args_.length; j++) {
                            var arg = `${path}.${args_[j]}`;
                            args.push($(document.getElementById(arg)).val());
                        }
                    }
                    element_path = path_.split('.');
                    method = element_path.pop();
                    element_path = element_path.join('.');
                    $.ajax({
                        url: "/elements/" + element_path,
                        type: "POST",
                        data: JSON.stringify({method: method, args: args}),
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (response) {
                            if (method == 'get_image()') {
                                showImage(response.result);
                            } else {
                                alert(response.result);
                            }
                        },
                        error: function (xhr, status, error) {
                            alert('Access denied');
                        }
                    });
                });

                li.append(button);
                methodsList.append(li);
            }
            ul.append(methodsList);
        }

        // Check for subsections
        if (section.hasOwnProperty("elements")) {
            buildElementsTable(section.elements, ul, path);
        }
    }
}

$.get('/get_user_info', function (data) {
    if (data) {
        $('#username').text(data.username);
        $('#email').text(data.email);
    }
});
