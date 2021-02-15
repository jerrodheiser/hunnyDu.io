import React, {useContext} from 'react';
import {Link, NavLink} from 'react-router-dom';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from 'react-bootstrap/NavDropdown';
import {HunnyduContext} from './Context/index';


// Component to display header.
const Header = () => {

  // Declare context api data.
  const {isAuthenticated, actions, isLeader, familyName, id} = useContext(HunnyduContext);

  // Return component jsx.
  // All links provided here are Bootstrap links configured as react-router-dom
  //  Links.  This is necessary because the Bootstrap links reload the page,
  //  whereas the react-router-dom links navigate without reloading.
  // Header navigation links are displayed based on user's session.
  return (
    <Navbar collapseOnSelect bg="dark" variant="dark" expand="lg">
      <Navbar.Brand as={Link} to="/" >hunnyDu</Navbar.Brand>
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Navbar.Collapse id="basic-navbar-nav" className="justify-content-end">
        <Nav className="mr-auto justify-content-end">
          {isAuthenticated
            ? <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
            : ''
          }
          {isLeader
            ? <Nav.Link as={Link} to="/newtask">New Task</Nav.Link>
            : ''
          }
          {isAuthenticated
            ? <NavDropdown title="Profile" id="basic-nav-dropdown">
                <NavDropdown.Item as={Link} to={`/viewProfile/${id}`}>View</NavDropdown.Item>
                <NavDropdown.Divider />
                <NavDropdown.Item onClick={actions.logoutUser}>Logout</NavDropdown.Item>
              </NavDropdown>
            : ''
          }
          {isAuthenticated
            ? <NavDropdown title="Family" id="basic-nav-dropdown">
                {familyName === ''
                  ? <NavDropdown.Item as={Link} to="/newFamily">Create a Family</NavDropdown.Item>
                  : <NavDropdown.Item as={Link} to="/viewFamily">View Family</NavDropdown.Item>
                }
                {isLeader
                  ?
                    <>
                      <NavDropdown.Divider />
                      <NavDropdown.Item as={Link} to="/sendJoinRequest">Add Members</NavDropdown.Item>
                      <NavDropdown.Item as={Link} to="/managefamily">Manage</NavDropdown.Item>
                    </>
                  : ''
                }
              </NavDropdown>
            : ''
          }
        </Nav>
        <Nav>
          {isAuthenticated
            ? <Nav.Link onClick={actions.logoutUser}>Logout</Nav.Link>
            : <Nav.Link as={NavLink} to="/login">Login</Nav.Link>
          }
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
}


export default Header;
