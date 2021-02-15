import React, {useContext, useEffect, useState} from 'react';
import TaskCard from './TaskCard';
import {HunnyduContext} from './Context/index';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Spinner from 'react-bootstrap/Spinner';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Accordion from 'react-bootstrap/Accordion';
import Button from 'react-bootstrap/Button';


// Component that displays a user's/family's tasks.
const Dashboard = () => {

  // Declare context api data.
  const {tasks, actions, familyName, familyTasks, isLeader} = useContext(HunnyduContext);

  // Declare state variable for which tasks are displayed (individual's vice
  //  entire family's).
  const [displayAll, setDisplayAll] = useState(isLeader ? true : false);

  // Declare state variable for status of loading data.
  const [isLoading, setIsLoading] = useState(true);


  // Refresh all tasks and clear loading state on initial render.
  useEffect (() => {
    actions.refreshTasks()
      .then(res => {
        setIsLoading(false);
      });
  },[]);


  // Return component jsx.
  return (
    <Container>
      {familyName
        ?
          <>
          <h1 className="pageTitle" >
            {familyName} - {displayAll
                            ? 'Family Dashboard'
                            : 'Your Dashboard'}
          </h1>
          { // Renders either a loading display, or tasks if loading is complete.
            isLoading
              ?
                <Col lg className="loading-visual">
                  <Row>
                    <Spinner animation="grow" role="status">
                      <span className="sr-only">Loading...</span>
                    </Spinner>
                  </Row>
                </Col>
              :
                <>
                  {// Renders tasks is present, otherwise a "no tasks" message.
                    tasks[0] || familyTasks[0]
                    ?
                      <>
                        <Button variant="primary" onClick={()=>setDisplayAll(!displayAll)}>
                          {displayAll
                            ? 'Show Your Tasks'
                            : 'Show Family\'s Tasks'
                          }
                        </Button>
                        <Accordion>
                          {/*
                            Bootstrap's event_index cannot be 0.
                          */}
                          {displayAll
                            ? familyTasks.map( (task, index) =>
                                <TaskCard
                                  task={task}
                                  event_index={index+1}
                                  key={index.toString()}
                                  displayingAll={displayAll}
                                />
                              )
                            : tasks.map( (task, index) =>
                                <TaskCard
                                  task={task}
                                  event_index={index+1}
                                  key={index.toString()}/>
                              )
                          }
                        </Accordion>
                      </>
                    :
                      <p>No tasks to display.</p>
                  }
                </>
          }
        </>
      :
        <>
          <Jumbotron>
            <h1>You are not currently part of a family.</h1>
            <p>
              Other family leaders can let you into their family, or you can
              <a href='/newFamily'> click here </a> to start your own.
            </p>
          </Jumbotron>
        </>
      }
    </Container>
  );
}


export default Dashboard;
