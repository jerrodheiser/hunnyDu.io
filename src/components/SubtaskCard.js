import React, { useContext } from 'react';
import { HunnyduContext } from './Context/index';
import ListGroup from 'react-bootstrap/ListGroup';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';


// Component that displays a subtask, and its complete/uncomplete buttons.
const SubtaskCard = (props) => {

  // Declare context api data and props.
  const {actions} = useContext(HunnyduContext);
  const {subtask, overdue, disabled} = props;
  const {is_complete, subtask_name, id} = subtask;


  // Return component jsx.
  return (
    <ListGroup.Item
    variant={is_complete ? "light" : (overdue ? "danger" : "")}
    >
      <Row>
        <Col>
          <div className={is_complete ? "subtaskComplete" : ""}>{subtask_name}</div>
        </Col>
        <Col xs lg="2">
          {disabled
            ? ''
            : <Button
                variant={"danger"}
                block
                onClick={()=>(actions.deleteSubtask(id))}>
                  {"Delete"}
                </Button>
          }
        </Col>
        <Col xs lg="2">
          <Button
          variant={is_complete ? "warning" : "success"}
          block
          onClick={()=>(actions.subtaskComplete(id))}>
            {is_complete ? "undo" : "complete"}
          </Button>
        </Col>
      </Row>
    </ListGroup.Item>
  );
}


export default SubtaskCard;
