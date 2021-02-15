import React, { useContext, useState, useRef } from 'react';
import { HunnyduContext } from './Context/index';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';


// Form used to create a new subtask.
const NewSubtaskForm = (props) => {

  // Declare context api data adn props.
  const {actions} = useContext(HunnyduContext);
  const {disabled} = props;

  // Declare state variable for handling form validation.
  const [hasBeenValidated, setHasBeenValidated] = useState(false);

  // Declare form refs.
  const stName = useRef();


  // Method to handle form submission.
  const handleSubmit = (e) => {
    e.preventDefault();
    setHasBeenValidated(true);
    let form = e.currentTarget;
    // Validate that required fields contain data.
    if (form.checkValidity() === false) {
      e.stopPropagation();
    } else {
      // No response data sent back to the user.
      actions.addSubtask(props.task_id,stName.current.value);
      e.currentTarget.reset();
      setHasBeenValidated(false);
    }
  }


  // Return component jsx.
  return(
    <Form
    noValidate
    validated={hasBeenValidated}
    className="subtaskForm"
    onSubmit={handleSubmit} >
      <Row>
        <Col>
          <Form.Control
          required
          placeholder="Enter a new subtask."
          ref={stName} />
          <Form.Control.Feedback type="invalid">Please provide a subtask.</Form.Control.Feedback>
          <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
        </Col>
        <Col>
          <Button variant={"success"} type={"submit"} disabled={disabled}>
            Add
          </Button>
        </Col>
      </Row>
    </Form>
  );
}


export default NewSubtaskForm;
