import { useEffect, useState } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow , MenuItem, FormControl, InputLabel, Select, Box, Button} from '@mui/material';



export default function LazyTable({route, columns, defaultPageSize, rowsPerPageOptions, onYearChange, onPositionChange, onSelectedChange}){
    // 
    const [data, setData] = useState([]);

    const [page, setPage] = useState(1); // 1 indexed
    const [pageSize, setPageSize] = useState(defaultPageSize ?? 10);
    const [draftYear, setDraftYear] = useState(2024);
    const [position, setPosition] = useState('WR');
    const [attribute, setAttrib] = useState('classification');


      // Now notice the dependency array contains route, page, pageSize, since we
  // need to re-fetch the data if any of these values change
  useEffect(() => {
    console.log(page, ' page', pageSize, ' page size');
    console.log(route, ' route FETCHING');
    // fetch(`${route}?page=${page}&page_size=${pageSize}`)

    fetch(`${route}`)
      .then(res => res.json())
      .then(resJson => {
    // Check if resJson is an array, otherwise look for players property
        const dataArray = Array.isArray(resJson) ? resJson : resJson.players || [];
        setData(dataArray);
    });
    
    
  }, [route, page, pageSize, attribute]);


  const handleChangePage = (e, newPage) => {
    // Can always go to previous page (TablePagination prevents negative pages)
    // but only fetch next page if we haven't reached the end (currently have full page of data)
    if (newPage < page || data.length === pageSize) {
      // Note that we set newPage + 1 since we store as 1 indexed but the default pagination gives newPage as 0 indexed
      setPage(newPage + 1);
    }
  }

  const handleChangePageSize = (e) => {
    // when handling events such as changing a selection box or typing into a text box,
    // the handler is called with parameter e (the event) and the value is e.target.value
    const newPageSize = e.target.value;
    setPageSize(newPageSize);
    setPage(1);
    // TODO (TASK 18): set the pageSize state variable and reset the current page to 1
  }


    // custom cell render
    const defaultRenderCell = (col, row) => {
        return <div>{row[col.field]}</div>;
    }

    const yearChange = (newYear) => {
      const year = newYear.target.value;
      setDraftYear(year);
      onYearChange(year);
    };

    const positionChange = (newPos) => {
      const p = newPos.target.value;
      setPosition(p);
      onPositionChange(p);
    }

    function attributeChange(value){
      const a = value;
      if(attribute == a){
        setAttrib('classification');
        onSelectedChange('classification');
      }
      else{
        setAttrib(a);
        onSelectedChange(a);
      }
    }

    function getRandomColor(classification) {
      if(classification == 'All Pro'){
        return '#308942';
      }else if(classification == 'Starter'){
        return '#1349cc';
      } else if(classification == 'Below Average Starter'){
        return '#071249';
      }
      return '#010301';
      
    }


   return(
     <TableContainer>
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, my: 4 }}>
      <FormControl sx={{ m: 1, minWidth: 120 }}>
        <InputLabel id="demo-simple-select-helper-label">Year</InputLabel>
        <Select
          labelId="demo-simple-select-helper-label"
          id="demo-simple-select-helper"
          value={draftYear}
          label="Year"
          onChange={yearChange}
        >
          <MenuItem value="">
            {/* <em>None</em> */}
          </MenuItem>
          <MenuItem value={2025}>2025</MenuItem>
          <MenuItem value={2024}>2024</MenuItem>
          <MenuItem value={2023}>2023</MenuItem>
          <MenuItem value={2022}>2022</MenuItem>
          <MenuItem value={2021}>2021</MenuItem>
          <MenuItem value={2020}>2020</MenuItem>
          <MenuItem value={2019}>2019</MenuItem>
          <MenuItem value={2018}>2018</MenuItem>
          <MenuItem value={2017}>2017</MenuItem>
          <MenuItem value={2016}>2016</MenuItem>
        </Select>
      </FormControl>
      <FormControl sx={{ m: 1, minWidth: 120 }}>
        <InputLabel id="demo-simple-select-helper-label2">Position</InputLabel>
        <Select
          labelId="demo-simple-select-helper-label2"
          id="demo-simple-select-helper2"
          value={position}
          label="Position"
          onChange={positionChange}
        >
          <MenuItem value="">
          </MenuItem>
          <MenuItem value={'QB'}>QB</MenuItem>
          <MenuItem value={'RB'}>RB</MenuItem>
          <MenuItem value={'WR'}>WR</MenuItem>
          <MenuItem value={'TE'}>TE</MenuItem>
        </Select>
      </FormControl>
      </Box>
        <Table>
            <TableHead>
                <TableRow>
                    {columns.map(col => <TableCell key={col.headerName}>
                      <Button onClick={()=> attributeChange(col.headerName)} style={{ color: 'black', textTransform: 'none' }}>
                      {col.headerName}
                      </Button>
                      </TableCell>)}
                </TableRow>
            </TableHead>
            <TableBody>
                {data.map((row, idx) =>
                    <TableRow key={idx}>
                        {
                            columns.map( col => 
                            <TableCell key={col.headerName} sx={{ backgroundColor: getRandomColor(row['classification']), color: 'white' }}>
                            {col.renderCell ? col.renderCell(row) : defaultRenderCell(col, row)}
                            </TableCell>
                            )
                        }
                    </TableRow>
                )}
            </TableBody>
        </Table>
       
     </TableContainer>
   ) 
}