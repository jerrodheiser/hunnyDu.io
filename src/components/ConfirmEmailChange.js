import React, { useContext } from 'react';
import { HunnyduContext } from './Context/index';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Spinner from 'react-bootstrap/Spinner';


// Component to handle confirming an updated email address.
// Component is accessed by a link sent in an email to confirm email address
//  changes.
const ConfirmEmailChange = (props) => {

  // Declare context api data.
  const {actions} = useContext(HunnyduContext);

  // Declare dynamic url token.
  const {match} = props
  const token = match.params.token;


  // Method to handle confirming the provided token.
  // User is always directed to '/' after processing.
  actions.confirmChangeEmail(token)
    .then(res => {
      if (res) {
        if (res.status === 200) {
          // Returned response is code 200 for successful email change.
          console.log('Successful email change.');
        }
        else if (res.status === 207) {
          // Returned response is code 207 for unavailable email address.
          console.log('Email address not available.');
        }
      } else {
        // Returned response is code 401 for unauthorized (invalid token).
        console.log('Failed confirmation.');
      }
      props.history.push('/');
    })


  // Return component jsx.
  // Component renders a loading wheel until redirected.
  return(
    <Container className="loading-visual">
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


export default ConfirmEmailChange;
