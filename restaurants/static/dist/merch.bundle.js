/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./restaurants/static/js/subpages/merch.js":
/*!*************************************************!*\
  !*** ./restaurants/static/js/subpages/merch.js ***!
  \*************************************************/
/***/ (() => {

eval("document.addEventListener('DOMContentLoaded', function () {\n  fetch('{% url \"get_product_templates\" business_details.subdirectory %}').then(function (response) {\n    return response.json();\n  }).then(function (data) {\n    var select = document.getElementById('templateSelect');\n    data.templates.forEach(function (template) {\n      var option = document.createElement('option');\n      option.value = template.id;\n      option.textContent = \"\".concat(template.name, \" - \").concat(template.type);\n      select.appendChild(option);\n    });\n  })[\"catch\"](function (error) {\n    return console.error('Error loading templates:', error);\n  });\n});\nfunction openProductModal() {\n  document.getElementById('productModal').classList.remove('hidden');\n}\nfunction closeProductModal() {\n  document.getElementById('productModal').classList.add('hidden');\n}\nfunction editProduct(productId) {\n  // Implement edit functionality\n  console.log('Editing product:', productId);\n}\n\n// Close modal when clicking outside\nwindow.onclick = function (event) {\n  var modal = document.getElementById('productModal');\n  if (event.target == modal) {\n    closeProductModal();\n  }\n};//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9yZXN0YXVyYW50cy9zdGF0aWMvanMvc3VicGFnZXMvbWVyY2guanMiLCJuYW1lcyI6WyJkb2N1bWVudCIsImFkZEV2ZW50TGlzdGVuZXIiLCJmZXRjaCIsInRoZW4iLCJyZXNwb25zZSIsImpzb24iLCJkYXRhIiwic2VsZWN0IiwiZ2V0RWxlbWVudEJ5SWQiLCJ0ZW1wbGF0ZXMiLCJmb3JFYWNoIiwidGVtcGxhdGUiLCJvcHRpb24iLCJjcmVhdGVFbGVtZW50IiwidmFsdWUiLCJpZCIsInRleHRDb250ZW50IiwiY29uY2F0IiwibmFtZSIsInR5cGUiLCJhcHBlbmRDaGlsZCIsImVycm9yIiwiY29uc29sZSIsIm9wZW5Qcm9kdWN0TW9kYWwiLCJjbGFzc0xpc3QiLCJyZW1vdmUiLCJjbG9zZVByb2R1Y3RNb2RhbCIsImFkZCIsImVkaXRQcm9kdWN0IiwicHJvZHVjdElkIiwibG9nIiwid2luZG93Iiwib25jbGljayIsImV2ZW50IiwibW9kYWwiLCJ0YXJnZXQiXSwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsid2VicGFjazovL3N0YXRpYy8uL3Jlc3RhdXJhbnRzL3N0YXRpYy9qcy9zdWJwYWdlcy9tZXJjaC5qcz80ZWYzIl0sInNvdXJjZXNDb250ZW50IjpbImRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoJ0RPTUNvbnRlbnRMb2FkZWQnLCBmdW5jdGlvbigpIHtcclxuICAgIGZldGNoKCd7JSB1cmwgXCJnZXRfcHJvZHVjdF90ZW1wbGF0ZXNcIiBidXNpbmVzc19kZXRhaWxzLnN1YmRpcmVjdG9yeSAlfScpXHJcbiAgICAgICAgLnRoZW4ocmVzcG9uc2UgPT4gcmVzcG9uc2UuanNvbigpKVxyXG4gICAgICAgIC50aGVuKGRhdGEgPT4ge1xyXG4gICAgICAgICAgICBjb25zdCBzZWxlY3QgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgndGVtcGxhdGVTZWxlY3QnKTtcclxuICAgICAgICAgICAgZGF0YS50ZW1wbGF0ZXMuZm9yRWFjaCh0ZW1wbGF0ZSA9PiB7XHJcbiAgICAgICAgICAgICAgICBjb25zdCBvcHRpb24gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdvcHRpb24nKTtcclxuICAgICAgICAgICAgICAgIG9wdGlvbi52YWx1ZSA9IHRlbXBsYXRlLmlkO1xyXG4gICAgICAgICAgICAgICAgb3B0aW9uLnRleHRDb250ZW50ID0gYCR7dGVtcGxhdGUubmFtZX0gLSAke3RlbXBsYXRlLnR5cGV9YDtcclxuICAgICAgICAgICAgICAgIHNlbGVjdC5hcHBlbmRDaGlsZChvcHRpb24pO1xyXG4gICAgICAgICAgICB9KTtcclxuICAgICAgICB9KVxyXG4gICAgICAgIC5jYXRjaChlcnJvciA9PiBjb25zb2xlLmVycm9yKCdFcnJvciBsb2FkaW5nIHRlbXBsYXRlczonLCBlcnJvcikpO1xyXG59KTtcclxuXHJcbmZ1bmN0aW9uIG9wZW5Qcm9kdWN0TW9kYWwoKSB7XHJcbiAgICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgncHJvZHVjdE1vZGFsJykuY2xhc3NMaXN0LnJlbW92ZSgnaGlkZGVuJyk7XHJcbn1cclxuXHJcbmZ1bmN0aW9uIGNsb3NlUHJvZHVjdE1vZGFsKCkge1xyXG4gICAgZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3Byb2R1Y3RNb2RhbCcpLmNsYXNzTGlzdC5hZGQoJ2hpZGRlbicpO1xyXG59XHJcblxyXG5mdW5jdGlvbiBlZGl0UHJvZHVjdChwcm9kdWN0SWQpIHtcclxuICAgIC8vIEltcGxlbWVudCBlZGl0IGZ1bmN0aW9uYWxpdHlcclxuICAgIGNvbnNvbGUubG9nKCdFZGl0aW5nIHByb2R1Y3Q6JywgcHJvZHVjdElkKTtcclxufVxyXG5cclxuLy8gQ2xvc2UgbW9kYWwgd2hlbiBjbGlja2luZyBvdXRzaWRlXHJcbndpbmRvdy5vbmNsaWNrID0gZnVuY3Rpb24oZXZlbnQpIHtcclxuICAgIGNvbnN0IG1vZGFsID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3Byb2R1Y3RNb2RhbCcpO1xyXG4gICAgaWYgKGV2ZW50LnRhcmdldCA9PSBtb2RhbCkge1xyXG4gICAgICAgIGNsb3NlUHJvZHVjdE1vZGFsKCk7XHJcbiAgICB9XHJcbn0iXSwibWFwcGluZ3MiOiJBQUFBQSxRQUFRLENBQUNDLGdCQUFnQixDQUFDLGtCQUFrQixFQUFFLFlBQVc7RUFDckRDLEtBQUssQ0FBQyxpRUFBaUUsQ0FBQyxDQUNuRUMsSUFBSSxDQUFDLFVBQUFDLFFBQVE7SUFBQSxPQUFJQSxRQUFRLENBQUNDLElBQUksQ0FBQyxDQUFDO0VBQUEsRUFBQyxDQUNqQ0YsSUFBSSxDQUFDLFVBQUFHLElBQUksRUFBSTtJQUNWLElBQU1DLE1BQU0sR0FBR1AsUUFBUSxDQUFDUSxjQUFjLENBQUMsZ0JBQWdCLENBQUM7SUFDeERGLElBQUksQ0FBQ0csU0FBUyxDQUFDQyxPQUFPLENBQUMsVUFBQUMsUUFBUSxFQUFJO01BQy9CLElBQU1DLE1BQU0sR0FBR1osUUFBUSxDQUFDYSxhQUFhLENBQUMsUUFBUSxDQUFDO01BQy9DRCxNQUFNLENBQUNFLEtBQUssR0FBR0gsUUFBUSxDQUFDSSxFQUFFO01BQzFCSCxNQUFNLENBQUNJLFdBQVcsTUFBQUMsTUFBQSxDQUFNTixRQUFRLENBQUNPLElBQUksU0FBQUQsTUFBQSxDQUFNTixRQUFRLENBQUNRLElBQUksQ0FBRTtNQUMxRFosTUFBTSxDQUFDYSxXQUFXLENBQUNSLE1BQU0sQ0FBQztJQUM5QixDQUFDLENBQUM7RUFDTixDQUFDLENBQUMsU0FDSSxDQUFDLFVBQUFTLEtBQUs7SUFBQSxPQUFJQyxPQUFPLENBQUNELEtBQUssQ0FBQywwQkFBMEIsRUFBRUEsS0FBSyxDQUFDO0VBQUEsRUFBQztBQUN6RSxDQUFDLENBQUM7QUFFRixTQUFTRSxnQkFBZ0JBLENBQUEsRUFBRztFQUN4QnZCLFFBQVEsQ0FBQ1EsY0FBYyxDQUFDLGNBQWMsQ0FBQyxDQUFDZ0IsU0FBUyxDQUFDQyxNQUFNLENBQUMsUUFBUSxDQUFDO0FBQ3RFO0FBRUEsU0FBU0MsaUJBQWlCQSxDQUFBLEVBQUc7RUFDekIxQixRQUFRLENBQUNRLGNBQWMsQ0FBQyxjQUFjLENBQUMsQ0FBQ2dCLFNBQVMsQ0FBQ0csR0FBRyxDQUFDLFFBQVEsQ0FBQztBQUNuRTtBQUVBLFNBQVNDLFdBQVdBLENBQUNDLFNBQVMsRUFBRTtFQUM1QjtFQUNBUCxPQUFPLENBQUNRLEdBQUcsQ0FBQyxrQkFBa0IsRUFBRUQsU0FBUyxDQUFDO0FBQzlDOztBQUVBO0FBQ0FFLE1BQU0sQ0FBQ0MsT0FBTyxHQUFHLFVBQVNDLEtBQUssRUFBRTtFQUM3QixJQUFNQyxLQUFLLEdBQUdsQyxRQUFRLENBQUNRLGNBQWMsQ0FBQyxjQUFjLENBQUM7RUFDckQsSUFBSXlCLEtBQUssQ0FBQ0UsTUFBTSxJQUFJRCxLQUFLLEVBQUU7SUFDdkJSLGlCQUFpQixDQUFDLENBQUM7RUFDdkI7QUFDSixDQUFDIiwiaWdub3JlTGlzdCI6W119\n//# sourceURL=webpack-internal:///./restaurants/static/js/subpages/merch.js\n");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval-source-map devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./restaurants/static/js/subpages/merch.js"]();
/******/ 	
/******/ })()
;