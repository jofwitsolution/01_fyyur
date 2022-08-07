const deleteVenue = document.getElementById("delete-venue");
deleteVenue.onclick = function (e) {
  venueId = e.target.dataset.id;
  console.log("delete clicked");
  console.log(venueId);
  fetch(`/venues/${venueId}`, {
    method: "DELETE",
  })
    .then(function () {
      window.location = "/";
    })
    .catch(function (e) {
      console.error(e);
    });
};
