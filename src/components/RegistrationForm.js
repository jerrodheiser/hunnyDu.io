import React, { useContext, useState, useRef } from 'react';
import { HunnyduContext } from './Context/index';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';


// Form used to register new user information.
const RegistrationForm = (props) => {

  // Declare context api data.
  const {actions} = useContext(HunnyduContext);

  // // Declare state variables for handling form validation.
  const [hasBeenValidated, setHasBeenValidated] = useState(false);
  const [unameAvail, setUnameAvail] = useState(true);
  const [validEmail,setValidEmail] = useState(true);
  const [emailAvail, setEmailAvail] = useState(true);
  const [pwordMatch, setPwordMatch] = useState(true);

  // Declare form refs.
  const username = useRef();
  const email = useRef();
  const password1 = useRef();
  const password2 = useRef();


  // Method to handle form submission.
  const handleSubmit = (e) => {
    e.preventDefault();
    // Reset validation variables.
    setUnameAvail(true);
    setValidEmail(true);
    setEmailAvail(true);
    setPwordMatch(true);
    let form = e.currentTarget;
    // Validate that required fields contain data.
    if (form.checkValidity() === false) {
      setHasBeenValidated(true);
      e.stopPropagation();
    } else {
      // Custom validation.
      if (password1.current.value !== password2.current.value) {
        setPwordMatch(false);
        setHasBeenValidated(true);
        password1.current.value = '';
        password2.current.value = '';
        e.stopPropagation();
      }
      if (!email.current.value.match('@') || !email.current.value.match('.')) {
        setValidEmail(false);
        email.current.value = '';
        setHasBeenValidated(true);
        e.stopPropagation();
      }
      else {
        actions.registerUser(username.current.value,
                             email.current.value,
                             password1.current.value)
          .then(res => {
            setHasBeenValidated(true);
            if (res.status === 207) {
              // Returned response is code 207 for unavailable username/email.
              if (res.data.username) {
                setUnameAvail(false);
                username.current.value = '';
              }
              if (res.data.email) {
                setEmailAvail(false);
                email.current.value = '';
              }
            }
            else if (res.status === 201) {
              // Returned response is code 201 for successful registration.
              props.history.push('/unconfirmed');
            }
          })
      }
    }
  }


  // Return component jsx.
  return(
    <Container className="loginForm-container">
      <Col lg>
        <Row className="justify-content-md-center">
          <Card>
            <Card.Body>
              <Card.Title>Register new account</Card.Title>
              <Form
              noValidate
              validated={hasBeenValidated}
              className="subtaskForm"
              onSubmit={handleSubmit}>
                <Form.Group as={Row}>
                  <Col>
                    <Form.Control
                    required
                    placeholder="Username"
                    ref={username}
                    />
                    <Form.Control.Feedback type="invalid">
                      {unameAvail
                        ? "Please provide a username."
                        : "Username is unavailable."
                      }
                    </Form.Control.Feedback>
                  </Col>
                </Form.Group>
                <Form.Group as={Row}>
                  <Col>
                    <Form.Control
                    required
                    placeholder="Email"
                    ref={email} />
                    <Form.Control.Feedback type="invalid">
                      {!validEmail
                        ? 'Please provide a valid email address.'
                        :
                          emailAvail
                          ? "Please provide an email address."
                          : "Email address is taken."
                      }
                    </Form.Control.Feedback>
                  </Col>
                </Form.Group>
                <Form.Group as={Row}>
                  <Col>
                    <Form.Control
                    required
                    type="password"
                    placeholder="Password"
                    ref={password1} />
                    <Form.Control.Feedback type="invalid">
                      {pwordMatch
                        ? 'Please provide a password.'
                        : 'Passwords do not match.'
                      }</Form.Control.Feedback>
                  </Col>
                </Form.Group>
                <Form.Group as={Row}>
                  <Col>
                    <Form.Control
                    required
                    type="password"
                    placeholder="Repeat password"
                    ref={password2}
                    />
                    <Form.Control.Feedback type="invalid">
                      {pwordMatch
                        ? 'Please provide a password.'
                        : 'Passwords do not match.'
                      }</Form.Control.Feedback>
                  </Col>
                </Form.Group>
                <Col>
                  <Button variant={"success"} type={"submit"}>
                    Register
                  </Button>
                </Col>
              </Form>
            </Card.Body>
          </Card>
        </Row>
      </Col>
    </Container>
  );
}


export default RegistrationForm;
