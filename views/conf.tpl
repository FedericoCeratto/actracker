% include('header.tpl')

            input {
                border: 1px solid #909090;
                background: #fafafa;
            }
            input:hover {
                background: #ffffff;
            }
            form {margin: 1em;}
        </style>
    </head>
    <body>
        % include('menu.tpl')
        <form method="post">
            <fieldset>
                <p>Existing rules</p>
            % n=0
            % for application_name in conf['classifiers']:
                % for regex, tags in conf['classifiers'][application_name]:
                    <input type="text" name="{{n}}_application_name" value="{{application_name}}"/>
                    <input type="text" name="{{n}}_regex" value="{{regex}}"/>
                    <input type="text" name="{{n}}_tags" value="{{','.join(tags)}}"/>
                    <br/>
                    % n+=1
                % end
            % end
                <br/>
                <p>New rule</p>
                <input type="text" name="{{n}}_application_name" value=""/>
                <input type="text" name="{{n}}_regex" value=""/>
                <input type="text" name="{{n}}_tags" value=""/>
                <br/>
                <br/>
            </fieldset>
            <p>
            <input type="submit" value="Save">
            {{msg}}</p>
        </form>

    </body>
</html>
