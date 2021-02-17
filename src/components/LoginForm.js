import React, { useContext, useState, useRef } from 'react';
import { HunnyduContext } from './Context/index';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';


// Form used to login with a user's provided credentials.
const LoginForm = (props) => {

  // Declare context api data.
  const {actions} = useContext(HunnyduContext);

  // Declare state variables for handling form validation.
  const [hasBeenValidated, setHasBeenValidated] = useState(false);
  const [wrongCombo, setWrongCombo] = useState(false);

  // Declare form refs.
  const email = useRef();
  const password = useRef();


  // Method to handle form submission.
  // Upon successful validation, user is redirected based on confirmed status.
  const handleSubmit = (e) => {
    e.preventDefault();
    // Reset validation variables.
    setWrongCombo(false);
    let form = e.currentTarget;
    // Validate that required fields contain data.
    if (form.checkValidity() === false) {
      setHasBeenValidated(true);
      e.stopPropagation();
    } else {
      actions.loginUser(email.current.value,password.current.value)
        .then (res => {
          if (res.status === 200) {
            // Returned response is code 200 for successful login.
            if (res.data.confirmed) {
              props.history.push('/');
            } else {
              // Returned response is code 400/401 for invalid credentials.
              props.history.push('/unconfirmed2');
            }
          } else {
            setHasBeenValidated(true);
            setWrongCombo(true);
            password.current.value = "";
          }
        });
    }
  }


  // Return component jsx.
  return(
    <Container className="loginForm-container">
      <Col lg>
        <Row className="justify-content-md-center">
          <Jumbotron>
            <h1>Welcome to hunnyDu!</h1>
            <p>The best way to assign and track household chores!</p>
          </Jumbotron>
        </Row>
        <Row className="justify-content-md-center">
          <Card>
            <Card.Body>
              <Card.Title>Login</Card.Title>
              <Form
              noValidate
              validated={hasBeenValidated}
              className="subtaskForm"
              onSubmit={handleSubmit}>
                <Form.Group as={Row}>
                  <Col>
                    <Form.Control
                    required
                    placeholder="Email"
                    ref={email} />
                    <Form.Control.Feedback type="invalid">
                      {wrongCombo
                        ? 'Please provide a valid email and password combination.'
                        : 'Please provide an email address.'
                      }
                    </Form.Control.Feedback>
                    <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
                  </Col>
                </Form.Group>
                <Form.Group as={Row}>
                  <Col>
                    <Form.Control
                    required
                    type="password"
                    placeholder="Password"
                    ref={password} />
                    <Form.Control.Feedback type="invalid">
                      {wrongCombo
                        ? 'Please provide a valid email and password combination.'
                        : 'Please provide a password.'
                      }</Form.Control.Feedback>
                    <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
                  </Col>
                </Form.Group>
                <Col>
                  <Button variant={"success"} type={"submit"}>
                    Login
                  </Button>
                </Col>
              </Form>
              <br/>
              <Card.Link href='/registration'>
                Want to join?</Card.Link>
              <Card.Link to="login" href='/sendPasswordReset'>
                Forgotten password?</Card.Link>
            </Card.Body>
          </Card>
        </Row>
      </Col>
    </Container>
  );
}


export default LoginForm;
