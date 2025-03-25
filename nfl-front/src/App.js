import { BrowserRouter, Routes, Route } from "react-router-dom";
import { CssBaseline, ThemeProvider } from '@mui/material'
import { indigo, amber } from '@mui/material/colors'
import { createTheme } from "@mui/material/styles";


// imports the homepage function from homepage
// don't have to import in curlys because it's the default function
import HomePage from './pages/homepage';
import NavBar from './components/NavBar';


import './App.css';


export const theme = createTheme({
  palette: {
    primary: indigo,
    secondary: amber,
  },
}
);

export default function App(){
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
