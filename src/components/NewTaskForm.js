import React, { useRef, useState, useContext } from 'react';
import { HunnyduContext } from './Context/index';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row'
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';


// Form used to create a new task.
const NewTaskForm = (props) => {

  // Declare context api data.
  const {actions, members} = useContext(HunnyduContext);

  // Declare state variable for handling form validation.
  const [hasBeenValidated, setHasBeenValidated] = useState(false);

  // Declare form refs.
  const taskname = useRef();
  const period = useRef();
  const assignee = useRef();

  // Declare state variable for determining amount of subtask form fields to
  //  render (max of 5).
  const [stAmount, setSTAmount] = useState(1);

  // Declare form refs for subtasks (max of 5).
  const st1 = useRef();
  const st2 = useRef();
  const st3 = useRef();
  const st4 = useRef();
  const st5 = useRef();

  // Declare the array of subtask refs, which will be mapped through.
  const stRefArray = [st1, st2, st3, st4, st5];

  // Declare an array of integers (of length stAmount) to be mapped through to
  //  render each subtask ref from stRefArray.
  let stMapArray = [...Array(stAmount).keys()];


  // Method to increase/decrease the amount of subtask form fields rendered.
  const handleSTAmountAdjust = (bool) => {
    if (bool) {
      setSTAmount(stAmount + 1);
    } else {
      if (stAmount > 1) {
        setSTAmount(stAmount -1);
      }
    }
  }


  // Method to combine all data present in subtask fields into an array string
  //  literal.
  const createStArraySL = () => {
    let returnArray = [];
    for (let i = 0; i < stAmount; i++) {
      returnArray[i] = stRefArray[i].current.value
    }
    return JSON.stringify(returnArray)
  }


  // Method to handle form submission.
  // Upon successful validation, user is redirected to '/'.
  const handleSubmit = (e) => {
    e.preventDefault();
    setHasBeenValidated(true);
    let form = e.currentTarget;
    // Validate that required fields contain data.
    if (form.checkValidity() === false) {
      e.stopPropagation();
    } else {
      const newTask = {
        taskname:taskname.current.value,
        period:period.current.value,
        assignee:assignee.current.value,
        subtasks:createStArraySL()
      }
      // No response data sent back to the user.
      actions.addTask(newTask);
      props.history.push('/');
    }
  }


  // Return component jsx.
  return (
    <Container >
      <h1 className="pageTitle"> Add New Task </h1>

      <Form noValidate validated={hasBeenValidated} onSubmit={handleSubmit}>
        <Form.Row>
          <Form.Label column="lg" lg={2}>
            Task Name:
          </Form.Label>
          <Col>
            <Form.Control
            required
            size="lg"
            type="text"
            placeholder="Enter task name"
            ref={taskname} />
            <Form.Control.Feedback type="invalid">Please provide a name.</Form.Control.Feedback>
            <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
          </Col>
        </Form.Row>
        <br />
        <Form.Row>
          <Form.Label column lg={2}>
            Assigned to:
          </Form.Label>
          <Col>
            <Form.Control
            required
            as="select"
            className="mr-sm-2"
            id="inlineFormCustomSelect"
            custom
            ref={assignee}>
              <option value="">Choose...</option>
              {members.map( (member,index) =>
                <option value={member.id} key={index.toString()}>
                  {member.isLeader
                    ? `${member.name} - Leader`
                    : `${member.name}`
                  }
                </option>
              )}
            </Form.Control>
            <Form.Control.Feedback type="invalid">Please select a user.</Form.Control.Feedback>
            <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
          </Col>
        </Form.Row>
        <br />
        <Form.Group as={Row}>
          <Form.Label as="legend" column sm={2}>
            Due:
          </Form.Label>
          <Col sm={10}>
            <Form.Control
            required
            as="select"
            className="mr-sm-2"
            id="inlineFormCustomSelect"
            custom
            ref={period}>
              <option value="">Choose...</option>
              <option value="d">Daily</option>
              <option value="w">Weekly</option>
              <option value="m">Monthly</option>
            </Form.Control>
            <Form.Control.Feedback type="invalid">Please select a period.</Form.Control.Feedback>
            <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
          </Col>
        </Form.Group>
        <Form.Row>
          <Form.Label column lg={2}>
            Subtasks (max of 5):
          </Form.Label>
        </Form.Row>

        {/*
            This will iterate through the stMapArray, which is an array of
              integers the length of the subtask amount.
            The stMapArray values are used as indices for associating stRefArray
              refs with rendered form fields.
        */}
        {stMapArray.map( iter =>
          <Form.Row key={iter.toString()}>
              <Form.Group>
                <Form.Control
                required
                type="text"
                placeholder="Subtask"
                ref={stRefArray[iter]}/>
                <Form.Control.Feedback type="invalid">Please provide a subtask.</Form.Control.Feedback>
                <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
              </Form.Group>
          </Form.Row>
        )}

        {/*
          These buttons handle increasing or decreasing the amount of subtasks.
          Amount of subtask form fields rendered must be >= 1 and <= 5.
        */}
        <Button
        variant="danger"
        size="sm"
        disabled={stAmount <= 1 ? true:false}
        onClick={()=>handleSTAmountAdjust(false)}>
          - </Button>

        <Button
        variant="success"
        size="sm"
        disabled={stAmount >= 5 ? true:false}
        onClick={()=>handleSTAmountAdjust(true)}>
          + </Button>

        {/* Submit button.  Submit function is handled in the form declaration. */}
        <Row className="justify-content-end">
          <Button variant="success" size="lg" type={"submit"}>Submit</Button>
        </Row>
      </Form>
      <br />
    </Container>
  );
}


export default NewTaskForm;
