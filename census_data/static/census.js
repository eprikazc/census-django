function addCommas(nStr)
{
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}

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
                $("#tabs").tabs();
            },
            error: function(data){
                $("#table-area").html("<p style='color:red'>Error loading data</p>");
            }
        });

    });

});