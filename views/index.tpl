% include('header.tpl')

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
            span.addrule {
                color: #333;
            }
            span.addrule:hover {
                color: #c03030;
            }

        </style>
        <meta http-equiv="refresh" content="2" >
    </head>
    <body>
        % include('menu.tpl')
        <table>
        % for perc, name, title, current, tags in app_usage:
            <tr>
                <td class="percentage">{{"%.1f" % perc}}</td>
                <td class="bar">
                    <div class="bar" style="width:{{int(perc)}}px">
                    </div>
                </td>
                <td>{{name}}</td>
                <td>
                    <a href="/conf">{{', '.join(tags)}}</a>
                </td>
                <td>{{'*' if current else ''}}
                <td>{{title}}</td>
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
        <p>Tot cnt: {{tot_cnt}}</p>
    </body>
    <script>
    $("span#addrule").click( function() {
    });
    </script>
</html>
