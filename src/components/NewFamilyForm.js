import React, { useRef, useState, useContext } from 'react';
import { HunnyduContext } from './Context/index';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row'
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';


// Form used to create a new family.
const NewFamilyForm = (props) => {

  // Declare context api data.
  const {actions} = useContext(HunnyduContext);

  // Declare state variable for handling form validation.
  const [hasBeenValidated, setHasBeenValidated] = useState(false);

  // Declare form refs.
  const familyName = useRef();


  // Method to handle form submission.
  // Upon successful validation, user is redirected to '/'.
  const handleSubmit = (e) => {
    e.preventDefault();
    setHasBeenValidated(true);
    let form = e.currentTarget;
    if (form.checkValidity() === false) {
      e.stopPropagation();
    } else {
      actions.createFamily(familyName.current.value)
        .then(res => {
          if (res) {
            // Returned response is code 201 for successful family creation.
            if (res.status === 201) {
              actions.refreshFamily();
            }
          } else {
            // Returned response is code 400 for bad request.
            console.log('Failed family creation.');
          }
        })
        .finally(() => props.history.push('/'))
    }
  }


  // Return component jsx.
  return (
    <Container >
      <h1 className="pageTitle"> Enter your family's name: </h1>

      <Form
      noValidate
      validated={hasBeenValidated}
      className="subtaskForm"
      onSubmit={handleSubmit} >
        <Form.Group as={Row}>
          <Col>
            <Form.Control
            required
            placeholder="Family Name"
            ref={familyName} />
            <Form.Control.Feedback type="invalid">
              Please provide a family name.
            </Form.Control.Feedback>
            <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
          </Col>
        </Form.Group>
        <Row>
          <Button variant="success" size="md" type={"submit"}>
            Start using HunnyDu!
          </Button>
        </Row>
      </Form>
      <br />
    </Container>
  );
}


export default NewFamilyForm;
