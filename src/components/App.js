import React from 'react';
import {
  BrowserRouter,
  Route,
  Redirect,
  Switch
} from 'react-router-dom';
import '../App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Provider } from './Context/index';
import Header from './Header';
import PrivateRoute from './PrivateRoute';
import LeaderRoute from './LeaderRoute';
import Dashboard from './Dashboard';
import NotFound from './NotFound';
import NewTaskForm from './NewTaskForm';
import LoginForm from './LoginForm';
import ConfirmUser from './ConfirmUser';
import ConfirmInviteToken from './ConfirmInviteToken';
import RegistrationForm from './RegistrationForm';
import FamilyInviteForm from './FamilyInviteForm';
import ViewFamily from './ViewFamily';
import ViewProfile from './ViewProfile';
import ManageFamily from './ManageFamily';
import UnconfirmedFirst from './UnconfirmedFirst';
import UnconfirmedAgain from './UnconfirmedAgain';
import ChangeEmailForm from './ChangeEmailForm';
import ConfirmEmailChange from './ConfirmEmailChange';
import RequestPasswordResetForm from './RequestPasswordResetForm';
import PasswordResetForm from './PasswordResetForm';
import NewFamilyForm from './NewFamilyForm';
import ChangePasswordForm from './ChangePasswordForm';
import Container from 'react-bootstrap/Container';


// Defines the app contents.
const App = () => {
  return (
    <BrowserRouter>
      <Container fluid >
        <Provider>
          <Header />
            <Switch>
              <PrivateRoute exact path="/" render={()=>(<Redirect to="/dashboard" />)} />
              <PrivateRoute path="/dashboard" component={Dashboard} />
              <PrivateRoute path="/viewFamily" component={ViewFamily} />
              <LeaderRoute path="/manageFamily" component={ManageFamily} />
              <LeaderRoute path="/newTask" component={NewTaskForm} />
              <LeaderRoute path="/sendJoinRequest" component={FamilyInviteForm} />
              <Route path="/login" component={LoginForm} />
              <Route path="/registration" component={RegistrationForm} />
              <PrivateRoute path="/viewProfile/:id" component={ViewProfile} />
              <Route path="/unconfirmed1" component={UnconfirmedFirst} />
              <Route path="/unconfirmed2" component={UnconfirmedAgain} />
              <PrivateRoute path="/changeEmail" component={ChangeEmailForm} />
              <PrivateRoute path="/newFamily" component={NewFamilyForm} />
              <Route path="/sendPasswordReset" component={RequestPasswordResetForm} />
              <PrivateRoute path="/changePassword" component={ChangePasswordForm} />
              <Route path="/auth/confirmUser/:token" component={ConfirmUser} />
              <Route path="/auth/confirmInviteToken/:token" component={ConfirmInviteToken} />
              <Route path="/auth/confirmEmailChange/:token" component={ConfirmEmailChange} />
              <Route path="/auth/resetPassword/:token" component={PasswordResetForm} />
              <PrivateRoute component={NotFound} />
            </Switch>
        </Provider>
      </Container>
    </BrowserRouter>
  );
}


export default App;
