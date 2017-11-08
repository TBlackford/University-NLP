// Script needs to load as soon as page does
$.get("/api/universities", function(data) {
    var content = "";

    var unis = data.universities;

    for(var i = 0; i < unis.length; i++) {

        content += "<tr><th scope='row'>" + unis[i].rank + "</th>" +
            "<td>" + unis[i].name + "</td>" +
            "<td><a href='" + unis[i].website + "'>" + unis[i].website + "</a></td></tr>";
    }

    $("#uni_body").append(content);
});