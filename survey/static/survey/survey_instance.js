// main.js
var React = require('react');
var ReactDOM = require('react-dom');

var HelloWorld = React.createClass({
    render: function () {
        return (
            <p>
                Hello du, <input type="text" placeholder="Your name here"/>!
                It is {this.props.date.toTimeString()}
            </p>
        );
    }
});

setInterval(function () {
    ReactDOM.render(
        <HelloWorld date={new Date()}/>,
        document.getElementById('survey')
    );
}, 500);

//ReactDOM.render(
//    <h1>Hello, world!</h1>,
//    document.getElementById('survey')
//);