import React, { useContext } from 'react';
import SubtaskCard from './SubtaskCard';
import NewSubtaskForm from './NewSubtaskForm';
import { HunnyduContext } from './Context/index';
import Card from 'react-bootstrap/Card';
import Accordion from 'react-bootstrap/Accordion';
import ListGroup from 'react-bootstrap/ListGroup';


// Component that displays a task, and its associated subtasks.
const TaskCard = (props) => {

  // Declare context api data and props.
  const {actions, isLeader} = useContext(HunnyduContext);
  const {event_index, task, displayingAll} = props;
  const {taskname, next_due, overdue, subtasks, assignee} = task;


  // Return component jsx.
  // This renders each subtask, the NewSubtaskForm, and a link to delete the
  //  task.
  return (
    <Card
        bg={overdue ? "danger" : ""}
        text={overdue ? "white" : "black"}
    >
      <Accordion.Toggle as={Card.Header} eventKey={event_index}>
        {taskname} - due {next_due} {displayingAll ? `(${assignee})` : ''}
      </Accordion.Toggle>
      <Accordion.Collapse eventKey={event_index}>
        <Card.Body>
          <ListGroup >
            {subtasks.map((subtask, index) =>
              <SubtaskCard
              subtask={subtask}
              disabled={subtasks.length <= 1 ? true : false}
              overdue={overdue}
              key={index.toString()} />
            )}
          </ListGroup>
          {isLeader
            ? <ListGroup>
                {subtasks.length >= 5
                  ? ''
                  : <NewSubtaskForm task_id={task.id} />
                }
              </ListGroup>
            : ''
          }

          {/*
            The href='#' is included here so that the mouse pointer displays.
          */}
          {isLeader
            ? <Card.Link onClick={()=>actions.deleteTask(task.id)} href='#'>
              Delete Task</Card.Link>
            : ''
          }
        </Card.Body>
      </Accordion.Collapse>
    </Card>
  );
}


export default TaskCard;
