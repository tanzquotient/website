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
        )
    }
});

var QuestionScale = React.createClass({
    render: function () {
        return (
            <div class="form-group">
                <label for="exampleInputEmail1">Email address</label>
                <div class="radio">
                    <label>rarely<input type="radio" aria-label="..."/> </label>
                </div>
                <label><input type="radio" aria-label="..."/> </label>
                <label><input type="radio" aria-label="..."/> </label>
                <label><input type="radio" aria-label="..."/> Often </label>

                <div class="input-group">
                    <div class="input-group-addon">
                        <input type="checkbox" aria-label="..."/>
                    </div>
                    <input type="text" class="form-control" aria-label="..."/>
                </div>
            </div>
        )
    }
});

ReactDOM.render(
    <h1>Hello, world!</h1>,
    document.getElementById('survey')
);


