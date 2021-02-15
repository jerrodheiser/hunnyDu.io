import React, { useRef, useState, useContext, useEffect } from 'react';
import { HunnyduContext } from './Context/index';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row'
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';


// Form used to reset a user's password if forgotten.
const PasswordResetForm = (props) => {

  // Declare context api data.
  const {actions} = useContext(HunnyduContext);

  // Declare state variables for handling form validation.
  const [hasBeenValidated, setHasBeenValidated] = useState(false);
  const [pwordMatch, setPwordMatch] = useState(true);

  // Declare the token which was provided in the password reset email.
  const {match} = props
  const token = match.params.token;

  // Declare state variable
  const [isLoading, setIsLoading] = useState(true)

  // Creates refs for the other form fields.
  const password1 = useRef();
  const password2 = useRef()


  // Checks token validity on initial component render, and redirects if the
  //  token is invalid.
  useEffect (() => {
    actions.validateResetRequest(token)
      .then(res => {
        if (res) {
          if (res.status === 200) {
            // Returned response is code 200 for valid token.
            console.log('Successful confirmation!');
            setIsLoading(false);
          }
        }
        else {
          // Returned response is code 401 for invalid token.
          console.log('Invalid token.');
          props.history.push('/');
        }
      })
  },[]);


  // Method to handle form submission.
  const handleSubmit = (e) => {
    e.preventDefault();
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
      else {
        // No response data sent back to the user.
        actions.resetPassword(password1.current.value, token)
          .then(res => {
            if (res) {
              if (res.status === 200) {
                // Returned response is code 200 for successful change.
                console.log('Password updated.');
              }
            }
            else {
              // Returned response is code 401 for invalid token.
              console.log('Invalid token.');
            }
            props.history.push('/');
          })
      }
    }
  }


  // Return component jsx.
  return (
    !isLoading
      ?
        <Container >
          <h1 className="pageTitle"> Reset password: </h1>
          <Form
          noValidate
          validated={hasBeenValidated}
          className="subtaskForm"
          onSubmit={handleSubmit}>
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
                  }
                </Form.Control.Feedback>
              </Col>
            </Form.Group>
            <Form.Group as={Row}>
              <Col>
                <Form.Control
                required
                type="password"
                placeholder="Repeat password"
                ref={password2} />
                <Form.Control.Feedback type="invalid">
                  {pwordMatch
                    ? 'Please provide a password.'
                    : 'Passwords do not match.'
                  }</Form.Control.Feedback>
              </Col>
            </Form.Group>

            <Row>
              <Button variant="success" size="md" type={"submit"}>Reset Password</Button>
            </Row>
          </Form>
          <br />
        </Container>
      :
        <Col lg className="loading-visual">
          <Row>
            <Spinner animation="grow" role="status">
              <span className="sr-only">Loading...</span>
            </Spinner>
          </Row>
        </Col>
  );
}


export default PasswordResetForm;
