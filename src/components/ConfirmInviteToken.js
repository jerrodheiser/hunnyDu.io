import React, { useContext } from 'react';
import { HunnyduContext } from './Context/index';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Spinner from 'react-bootstrap/Spinner';


// Component to handle confirming a members invitation token.
// Component is accessed by a link sent in an invitation email.
const ConfirmInviteToken = (props) => {

  // Declare context api data.
  const {actions} = useContext(HunnyduContext);

  // Declare dynamic url token.
  const {match} = props
  const token = match.params.token;


  // Method to handle confirming the provided token.
  // User is always directed to '/' after processing.
  actions.confirmInviteToken(token)
    .then(res => {
      if (res) {
        if (res.status === 200) {
          // Returned response is code 200 for successful confirmation.
          console.log('Successful confirmation!');
        }
        else if (res.status === 404) {
          console.log('User not found.');
        }
      } else {
        // Returned response is code 401 for unauthorized (invalid token).
        console.log('Failed confirmation!');
      }
      props.history.push('/');
    })


  // Return component jsx.
  // Component renders a loading wheel until redirected.
  return(
    <Container className="loginForm-container">
      <Col lg>
        <Row className="justify-content-md-center">
          <Spinner animation="grow" role="status">
            <span className="sr-only">Loading...</span>
          </Spinner>
        </Row>
      </Col>
    </Container>
  );
}


export default ConfirmInviteToken;
