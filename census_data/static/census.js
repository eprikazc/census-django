$(function(){
    $("button.get_data").click(function(event){
        event.preventDefault();
        $("#table-area").html("");
        var geo_region_selected = $("option:selected", $(this).siblings("select"));
        $.ajax({
            url: "/stat/" + geo_region_selected.attr("value") + "/",
            dataType: "json",
            success: function(data){
                var table_data = _.template(
                    $("#template-table").html(),
                    {stat_data: data, area: geo_region_selected.text()}
                );
                $("#table-area").html(table_data);
            },
            error: function(data){
                $("#table-area").html("<p style='color:red'>Error loading data</p>");
            }
        });

    });

});