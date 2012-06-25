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
        $("#plot-area").html("");
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
                var chart;
                var chart_data = [];
                for (var i=1; i<data["VACANCY STATUS [8]"].length; i++)
                {
                    chart_data.push([data["VACANCY STATUS [8]"][i][1], parseFloat(data["VACANCY STATUS [8]"][i][2])]);
                }
                chart = new Highcharts.Chart({
                    chart: {
                        renderTo: 'plot-area',
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false
                    },
                    title: {
                        text: 'Vacancy status pie chart'
                    },
                    tooltip: {
                        formatter: function() {
                            return '<b>'+ this.point.name +'</b>: '+ this.y;
                        }
                    },
                    plotOptions: {
                        pie: {
                            animation: false,
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: true,
                                color: '#000000',
                                connectorColor: '#000000',
                                formatter: function() {
                                    return '<b>'+ this.point.name +'</b>: '+ this.y;
                                }
                            }
                        }
                    },
                    series: [{
                        type: 'pie',
                        name: 'Vacancy status',
                        data: chart_data
                    }]
                });

            },
            error: function(data){
                $("#table-area").html("<p style='color:red'>Error loading data</p>");
            }
        });

    });

});