import React, {useContext, useEffect, useState} from 'react';
import {HunnyduContext} from './Context/index';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Spinner from 'react-bootstrap/Spinner';
import ListGroup from 'react-bootstrap/ListGroup';


// Component that displays a user's profile.
const ViewProfile = (props) => {

  // Declare context api data.
  const {actions, id} = useContext(HunnyduContext);
  const {match} = props;
  const userId = parseInt(match.params.id);

  // Declare state variable for status of loading data.
  const [isLoading, setIsLoading] = useState(true);

  // Declare state variable for user.
  const [user, setUser] = useState();

  // Retrieve user information when userId is changed.
  useEffect (() => {
    actions.getProfile(userId)
      .then( res => {
        if (res) {
          // Returned response is code 200 for successful retrieval.
          if (res.status === 200) {
            setUser(res.data);
            setIsLoading(false);
          }
        } else {
          // Returned response is code 404 for user not found.
          console.log('User retrieval failed.')
          props.history.push('/');
        }
      });
  },[userId]);


  // Return component jsx.
  return (
    <Container>
      {isLoading
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
            <h1 className="pageTitle">{user.username}'s Profile</h1>
            <ListGroup variant='flush'>
              {userId === id
                ?
                  <>
                    <ListGroup.Item>{user.email} - <a href='/changeEmail'>
                        Change</a>
                    </ListGroup.Item>
                    <ListGroup.Item><a href='/changePassword'>
                        Change password</a>
                    </ListGroup.Item>
                  </>
                :
                  ''
              }
            </ListGroup>
            <br/>
            <h2> Tasks </h2>
            <ListGroup>
              {user.tasks.map((task, index) =>
                <ListGroup.Item key={index.toString()}>
                  {task.taskname}
                </ListGroup.Item>
              )}
            </ListGroup>
          </>
      }
    </Container>
  );
}


export default ViewProfile;
