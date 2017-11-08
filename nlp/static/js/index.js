Dropzone.autoDiscover = false;

$(function() {
    var upload_route = "/upload";
    var upload_div = "#fileupload";

    var dropzone = new Dropzone(upload_div, { url: upload_route});

    dropzone.on("success", function(file) {
        $(".uni_list").append("<option value=" + file.name + ">" + file.name + "</option>");
    });
});