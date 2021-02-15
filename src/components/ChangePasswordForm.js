import React, { useContext, useState, useRef } from 'react';
import { HunnyduContext } from './Context/index';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';


// Form used to process password changes when logged in.
const ChangePasswordForm = (props) => {

  // Declare context api data.
  const {actions} = useContext(HunnyduContext);

  // Declare state variables for handling form validation.
  const [hasBeenValidated, setHasBeenValidated] = useState(false);
  const [wrongPword, setWrongPword] = useState(false);
  const [pwordMatch, setPwordMatch] = useState(true);

  // Declare form refs.
  const passwordCurrent = useRef();
  const password1 = useRef();
  const password2 = useRef();


  // Method to handle form submission.
  // Upon successful validation, user is redirected to '/'.
  const handleSubmit = (e) => {
    e.preventDefault();
    // Reset validation variables.
    setPwordMatch(true);
    setWrongPword(false);
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
        actions.changePassword(passwordCurrent.current.value, password1.current.value)
          .then(res => {
            if (res) {
              if (res.status === 200) {
                // Returned response is code 200 for successful password change.
                console.log("Successful change.")
                props.history.push('/');
              }
            } else {
              // Returned response is code 401 for invalid password.
              setHasBeenValidated(true);
              setWrongPword(true);
              console.log('Failed change.')
              passwordCurrent.current.value = '';
            }
          })
      }
    }
  }


  // Return component jsx.
  return(
    <Container>
      <h1 className="pageTitle"> Change Password </h1>
      <Form noValidate validated={hasBeenValidated} onSubmit={handleSubmit}>
        <Form.Row>
          <Form.Label column lg={2}>
            Current Password:
          </Form.Label>
          <Col>
            <Form.Control
            required
            size="lg"
            type="password"
            placeholder="Current password"
            ref={passwordCurrent} />
            <Form.Control.Feedback type="invalid">
              {wrongPword
                ? 'Please provide a valid password.'
                : 'Please provide a valid password.'
              }
            </Form.Control.Feedback>
          </Col>
        </Form.Row>
        <br/>
        <Form.Row>
          <Form.Label column lg={2}>
            New Password:
          </Form.Label>
          <Col>
            <Form.Control
            required
            size="lg"
            type="password"
            placeholder="New password"
            ref={password1} />
            <Form.Control.Feedback type="invalid">
              {pwordMatch
                ? 'Please provide a valid password.'
                : 'Passwords must match.'
              }
            </Form.Control.Feedback>
          </Col>
        </Form.Row>
        <br/>
        <Form.Row>
          <Form.Label column lg={2}>
            Repeat New Password:
          </Form.Label>
          <Col>
            <Form.Control
            required
            size="lg"
            type="password"
            placeholder="Repeat new password"
            ref={password2} />
            <Form.Control.Feedback type="invalid">
              {pwordMatch
                ? 'Please provide a valid password.'
                : 'Passwords must match.'
              }
            </Form.Control.Feedback>
          </Col>
        </Form.Row>
        <br/>
        <Form.Row>
          <Button variant={"success"} type={"submit"}>
            Save Changes
          </Button>
        </Form.Row>
      </Form>
    </Container>
  );
}


export default ChangePasswordForm;
