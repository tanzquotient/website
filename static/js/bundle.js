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

setInterval(function () {
    ReactDOM.render(React.createElement(HelloWorld, { date: new Date() }), document.getElementById('survey'));
}, 500);

//ReactDOM.render(
//    <h1>Hello, world!</h1>,
//    document.getElementById('survey')
//);

},{"react":"react","react-dom":"react-dom"}]},{},[1])
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJzdXJ2ZXkvc3RhdGljL3N1cnZleS9zdXJ2ZXlfaW5zdGFuY2UuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7O0FDQ0EsSUFBSSxRQUFRLFFBQVEsT0FBUixDQUFSO0FBQ0osSUFBSSxXQUFXLFFBQVEsV0FBUixDQUFYOztBQUVKLElBQUksYUFBYSxNQUFNLFdBQU4sQ0FBa0I7OztBQUMvQixZQUFRLFlBQVk7QUFDaEIsZUFDSTs7OztZQUNjLCtCQUFPLE1BQUssTUFBTCxFQUFZLGFBQVksZ0JBQVosRUFBbkIsQ0FEZDs7WUFFVyxLQUFLLEtBQUwsQ0FBVyxJQUFYLENBQWdCLFlBQWhCLEVBRlg7U0FESixDQURnQjtLQUFaO0NBREssQ0FBYjs7QUFXSixZQUFZLFlBQVk7QUFDcEIsYUFBUyxNQUFULENBQ0ksb0JBQUMsVUFBRCxJQUFZLE1BQU0sSUFBSSxJQUFKLEVBQU4sRUFBWixDQURKLEVBRUksU0FBUyxjQUFULENBQXdCLFFBQXhCLENBRkosRUFEb0I7Q0FBWixFQUtULEdBTEgiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiLy8gbWFpbi5qc1xudmFyIFJlYWN0ID0gcmVxdWlyZSgncmVhY3QnKTtcbnZhciBSZWFjdERPTSA9IHJlcXVpcmUoJ3JlYWN0LWRvbScpO1xuXG52YXIgSGVsbG9Xb3JsZCA9IFJlYWN0LmNyZWF0ZUNsYXNzKHtcbiAgICByZW5kZXI6IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgcmV0dXJuIChcbiAgICAgICAgICAgIDxwPlxuICAgICAgICAgICAgICAgIEhlbGxvIGR1LCA8aW5wdXQgdHlwZT1cInRleHRcIiBwbGFjZWhvbGRlcj1cIllvdXIgbmFtZSBoZXJlXCIvPiFcbiAgICAgICAgICAgICAgICBJdCBpcyB7dGhpcy5wcm9wcy5kYXRlLnRvVGltZVN0cmluZygpfVxuICAgICAgICAgICAgPC9wPlxuICAgICAgICApO1xuICAgIH1cbn0pO1xuXG5zZXRJbnRlcnZhbChmdW5jdGlvbiAoKSB7XG4gICAgUmVhY3RET00ucmVuZGVyKFxuICAgICAgICA8SGVsbG9Xb3JsZCBkYXRlPXtuZXcgRGF0ZSgpfS8+LFxuICAgICAgICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnc3VydmV5JylcbiAgICApO1xufSwgNTAwKTtcblxuLy9SZWFjdERPTS5yZW5kZXIoXG4vLyAgICA8aDE+SGVsbG8sIHdvcmxkITwvaDE+LFxuLy8gICAgZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3N1cnZleScpXG4vLyk7Il19
