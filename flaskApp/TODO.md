```
- [X] Basic API description in readme
- [X] Create stub endpoints in flask
  - [X] TLE endpoints
  - [X] Passes endpoints
- [ ] Implement endpoints
  - [X] Get all TLEs
  - [X] Get multiple TLEs
  - [X] Get specific TLE
  - [X] Get passes for a single satellite
  - [X] Get passes for multiple satellites
  - [X] Get passes for all satellites
- [ ] additional features
  - [X] report TLE epoch with TLE
  - [X] limit number of days
  - [X] limit number of returned passes

Future
  - [ ] Detailed pass information
  

BUGS
- [ ] sunlit is parameter is ignored in getPasses
- [ ] fix api documentation to match the implementation, include schemas
- [ ] remove json in GET payload and move to URL parameters
