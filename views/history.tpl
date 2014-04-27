% include('header.tpl')

            div.day {
                width: 4px;
                border: 1px solid #888;
                float: left;
            }
            canvas{
                border: 1px dashed #aaa;
            }
        </style>
    </head>
    <script type="text/javascript">
        function drawShape(){
          // get the canvas element using the DOM
          var canvas = document.getElementById('mycanvas');

          // Make sure we don't execute when canvas isn't supported
          if (canvas.getContext){

            // use getContext to use the canvas for drawing
            var context = canvas.getContext('2d');
            context.beginPath();
            context.lineWidth = 2;
            context.lineCap = 'round';

            % from colorsys import hsv_to_rgb
            % tags_cols = []
            % for tagnum, t in enumerate(tags):
                % col = "#%02x%02x%02x" % tuple(int(x * 256) for x in hsv_to_rgb(.11 * tagnum % 1, .9, .9))
                % tags_cols.append((t, col))
                context.beginPath();
                context.moveTo(0, 0);
                context.strokeStyle = '{{col}}';
                % for n, (date, c) in enumerate(days):
                    % h =  400 - c[t] / 100
                    context.lineTo({{n*25}}, {{h}});
                % end
                context.stroke();
            % end
          }
        }
    </script>
    </head>
    <body onload="drawShape();">
        % include('menu.tpl')
        <canvas id="mycanvas" width="700" height="400"></canvas>
        <ul>
            % for t, col in tags_cols:
            <li style="color:{{col}};"><span style="color:#000;">{{t}}</span></li>
            % end
        </ul>
    </body>
</html>
