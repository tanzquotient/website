(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
// main.js
var React = require('react');
var ReactDOM = require('react-dom');

var HelloWorld = React.createClass({
    displayName: 'HelloWorld',

    render: function () {
        return React.createElement(
            'p',
            null,
            'Hello du, ',
            React.createElement('input', { type: 'text', placeholder: 'Your name here' }),
            '! It is ',
            this.props.date.toTimeString()
        );
    }
});

var QuestionScale = React.createClass({
    displayName: 'QuestionScale',

    render: function () {
        return React.createElement(
            'div',
            { 'class': 'form-group' },
            React.createElement(
                'label',
                { 'for': 'exampleInputEmail1' },
                'Email address'
            ),
            React.createElement(
                'div',
                { 'class': 'radio' },
                React.createElement(
                    'label',
                    null,
                    'rarely',
                    React.createElement('input', { type: 'radio', 'aria-label': '...' }),
                    ' '
                )
            ),
            React.createElement(
                'label',
                null,
                React.createElement('input', { type: 'radio', 'aria-label': '...' }),
                ' '
            ),
            React.createElement(
                'label',
                null,
                React.createElement('input', { type: 'radio', 'aria-label': '...' }),
                ' '
            ),
            React.createElement(
                'label',
                null,
                React.createElement('input', { type: 'radio', 'aria-label': '...' }),
                ' Often '
            ),
            React.createElement(
                'div',
                { 'class': 'input-group' },
                React.createElement(
                    'div',
                    { 'class': 'input-group-addon' },
                    React.createElement('input', { type: 'checkbox', 'aria-label': '...' })
                ),
                React.createElement('input', { type: 'text', 'class': 'form-control', 'aria-label': '...' })
            )
        );
    }
});

ReactDOM.render(React.createElement(
    'h1',
    null,
    'Hello, world!'
), document.getElementById('survey'));

},{"react":"react","react-dom":"react-dom"}]},{},[1])
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJzdXJ2ZXkvc3RhdGljL3N1cnZleS9zdXJ2ZXlfaW5zdGFuY2UuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7O0FDQ0EsSUFBSSxRQUFRLFFBQVEsT0FBUixDQUFSO0FBQ0osSUFBSSxXQUFXLFFBQVEsV0FBUixDQUFYOztBQUVKLElBQUksYUFBYSxNQUFNLFdBQU4sQ0FBa0I7OztBQUMvQixZQUFRLFlBQVk7QUFDaEIsZUFDSTs7OztZQUNjLCtCQUFPLE1BQUssTUFBTCxFQUFZLGFBQVksZ0JBQVosRUFBbkIsQ0FEZDs7WUFFVyxLQUFLLEtBQUwsQ0FBVyxJQUFYLENBQWdCLFlBQWhCLEVBRlg7U0FESixDQURnQjtLQUFaO0NBREssQ0FBYjs7QUFXSixJQUFJLGdCQUFnQixNQUFNLFdBQU4sQ0FBa0I7OztBQUNsQyxZQUFRLFlBQVk7QUFDaEIsZUFDSTs7Y0FBSyxTQUFNLFlBQU4sRUFBTDtZQUNJOztrQkFBTyxPQUFJLG9CQUFKLEVBQVA7O2FBREo7WUFFSTs7a0JBQUssU0FBTSxPQUFOLEVBQUw7Z0JBQ0k7Ozs7b0JBQWEsK0JBQU8sTUFBSyxPQUFMLEVBQWEsY0FBVyxLQUFYLEVBQXBCLENBQWI7O2lCQURKO2FBRko7WUFLSTs7O2dCQUFPLCtCQUFPLE1BQUssT0FBTCxFQUFhLGNBQVcsS0FBWCxFQUFwQixDQUFQOzthQUxKO1lBTUk7OztnQkFBTywrQkFBTyxNQUFLLE9BQUwsRUFBYSxjQUFXLEtBQVgsRUFBcEIsQ0FBUDs7YUFOSjtZQU9JOzs7Z0JBQU8sK0JBQU8sTUFBSyxPQUFMLEVBQWEsY0FBVyxLQUFYLEVBQXBCLENBQVA7O2FBUEo7WUFTSTs7a0JBQUssU0FBTSxhQUFOLEVBQUw7Z0JBQ0k7O3NCQUFLLFNBQU0sbUJBQU4sRUFBTDtvQkFDSSwrQkFBTyxNQUFLLFVBQUwsRUFBZ0IsY0FBVyxLQUFYLEVBQXZCLENBREo7aUJBREo7Z0JBSUksK0JBQU8sTUFBSyxNQUFMLEVBQVksU0FBTSxjQUFOLEVBQXFCLGNBQVcsS0FBWCxFQUF4QyxDQUpKO2FBVEo7U0FESixDQURnQjtLQUFaO0NBRFEsQ0FBaEI7O0FBdUJKLFNBQVMsTUFBVCxDQUNJOzs7O0NBREosRUFFSSxTQUFTLGNBQVQsQ0FBd0IsUUFBeEIsQ0FGSiIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCIvLyBtYWluLmpzXG52YXIgUmVhY3QgPSByZXF1aXJlKCdyZWFjdCcpO1xudmFyIFJlYWN0RE9NID0gcmVxdWlyZSgncmVhY3QtZG9tJyk7XG5cbnZhciBIZWxsb1dvcmxkID0gUmVhY3QuY3JlYXRlQ2xhc3Moe1xuICAgIHJlbmRlcjogZnVuY3Rpb24gKCkge1xuICAgICAgICByZXR1cm4gKFxuICAgICAgICAgICAgPHA+XG4gICAgICAgICAgICAgICAgSGVsbG8gZHUsIDxpbnB1dCB0eXBlPVwidGV4dFwiIHBsYWNlaG9sZGVyPVwiWW91ciBuYW1lIGhlcmVcIi8+IVxuICAgICAgICAgICAgICAgIEl0IGlzIHt0aGlzLnByb3BzLmRhdGUudG9UaW1lU3RyaW5nKCl9XG4gICAgICAgICAgICA8L3A+XG4gICAgICAgIClcbiAgICB9XG59KTtcblxudmFyIFF1ZXN0aW9uU2NhbGUgPSBSZWFjdC5jcmVhdGVDbGFzcyh7XG4gICAgcmVuZGVyOiBmdW5jdGlvbiAoKSB7XG4gICAgICAgIHJldHVybiAoXG4gICAgICAgICAgICA8ZGl2IGNsYXNzPVwiZm9ybS1ncm91cFwiPlxuICAgICAgICAgICAgICAgIDxsYWJlbCBmb3I9XCJleGFtcGxlSW5wdXRFbWFpbDFcIj5FbWFpbCBhZGRyZXNzPC9sYWJlbD5cbiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPVwicmFkaW9cIj5cbiAgICAgICAgICAgICAgICAgICAgPGxhYmVsPnJhcmVseTxpbnB1dCB0eXBlPVwicmFkaW9cIiBhcmlhLWxhYmVsPVwiLi4uXCIvPiA8L2xhYmVsPlxuICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICAgIDxsYWJlbD48aW5wdXQgdHlwZT1cInJhZGlvXCIgYXJpYS1sYWJlbD1cIi4uLlwiLz4gPC9sYWJlbD5cbiAgICAgICAgICAgICAgICA8bGFiZWw+PGlucHV0IHR5cGU9XCJyYWRpb1wiIGFyaWEtbGFiZWw9XCIuLi5cIi8+IDwvbGFiZWw+XG4gICAgICAgICAgICAgICAgPGxhYmVsPjxpbnB1dCB0eXBlPVwicmFkaW9cIiBhcmlhLWxhYmVsPVwiLi4uXCIvPiBPZnRlbiA8L2xhYmVsPlxuXG4gICAgICAgICAgICAgICAgPGRpdiBjbGFzcz1cImlucHV0LWdyb3VwXCI+XG4gICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9XCJpbnB1dC1ncm91cC1hZGRvblwiPlxuICAgICAgICAgICAgICAgICAgICAgICAgPGlucHV0IHR5cGU9XCJjaGVja2JveFwiIGFyaWEtbGFiZWw9XCIuLi5cIi8+XG4gICAgICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICAgICAgICA8aW5wdXQgdHlwZT1cInRleHRcIiBjbGFzcz1cImZvcm0tY29udHJvbFwiIGFyaWEtbGFiZWw9XCIuLi5cIi8+XG4gICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgKVxuICAgIH1cbn0pO1xuXG5SZWFjdERPTS5yZW5kZXIoXG4gICAgPGgxPkhlbGxvLCB3b3JsZCE8L2gxPixcbiAgICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnc3VydmV5Jylcbik7XG5cblxuIl19
