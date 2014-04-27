% include('header.tpl')

            div.day {
                width: 4px;
                border: 1px solid #888;
                float: left;
            }
            canvas{
                border: 1px dashed #aaa;
            }
            div#xlabel {
                width: 700px;
            }
            div#xlabel div#right {
                float: right;
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
            context.lineWidth = 1;
            context.lineCap = 'round';

            context.beginPath();
            context.moveTo(0, 0);
            % x_samples_num = len(act)
            % x_distance_px = 700 / x_samples_num
            % for num, (x, y) in enumerate(act):
                context.lineTo({{num * x_distance_px}}, {{400 - ((400 * y)/max_val)}});
            % end
            context.stroke();
          }
        }
    </script>
        <meta http-equiv="refresh" content="2" >
    </head>
    <body onload="drawShape();">
        % include('menu.tpl')
        <canvas id="mycanvas" width="700" height="400"></canvas>
        <div id="xlabel">
            <div id="left">{{act[0][0]}}</div>
            <div id="right">{{act[-1][0]}}</div>
        </div>
    </body>
</html>
