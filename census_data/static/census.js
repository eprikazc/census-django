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

function generatePieChart(renderToElement, title, chartName, chartData){
    return new Highcharts.Chart({
        chart: {
            renderTo: renderToElement,
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: title
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
            name: chartName,
            data: chartData
        }]
    });
}

$(function(){
    $("button.get_data").click(function(event){
        event.preventDefault();
        $("#table-area").html("");
        $("#plot-area").html("");
        var geo_region_selected = $("option:selected", $(this).siblings("select"));
        var stat_url = "/stat/" + geo_region_selected.attr("value") + "/";
        $.ajax({
            url: stat_url,
            dataType: "json",
            success: function(data){
                var table_data = _.template(
                    $("#template-table").html(),
                    {stat_data: data, area: geo_region_selected.text(), pdf_report_url: stat_url + "?pdf"}
                );
                $("#table-area").html(table_data);
                $("#tabs").tabs();
                var chartData = [];
                data["VACANCY STATUS [8]"].forEach(function(value, index){
                    if (index != 0 ) chartData.push([value[1], parseFloat(value[2])]);
                });
                generatePieChart("vacancy-plot-area", "Vacancy status pie chart", "Vacancy status", chartData);
                chartData = [];
                data["TENURE [4]"].forEach(function(value, index){
                    if (index != 0 ) chartData.push([value[1], parseFloat(value[2])]);
                });
                generatePieChart("tenure-plot-area", "Tenure pie chart", "Tenure", chartData);
                chartData = [];
                data["RACE [8]"].forEach(function(value, index){
                    if (index != 0 ) chartData.push([value[1], parseFloat(value[2])]);
                });
                generatePieChart("race-plot-area", "Race pie chart", "Race", chartData);

            },
            error: function(data){
                $("#table-area").html("<p style='color:red'>Error loading data</p>");
            }
        });

    });

});