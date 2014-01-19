<html>
    <head>
        <title></title>
        <meta http-equiv="refresh" content="1" >
        <style>
            div.bar {
                height: 4px;
                border: 1px solid #888;
            }
            td.percentage {
                text-size: 80%;
            }
            td.bar {
                width: 100px;
            }

        </style>
    </head>
    <body>
        <table>
        % for k,v,v2 in app_usage:
            <tr>
                <td class="percentage">{{"%.1f" % k}}</td>
                <td class="bar">
                    <div class="bar" style="width:{{int(k)}}px">
                    </div>
                </td>
                <td>{{v}}</td>
                <td>{{v2}}</td>
            </tr>
        % end
        </table>
        <br/>
        <table>
        % for tag, perc in tags_summary:
            <tr>
                <td class="percentage">{{"%.1f" % perc}}</td>
                <td class="bar">
                    <div class="bar" style="width:{{int(perc)}}px">
                    </div>
                </td>
                <td>{{tag}}</td>
            </tr>
        % end
        </table>
    </body>
</html>
