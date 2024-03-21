# Import the required module for Invoke-RestMethod
Import-Module -Name Microsoft.PowerShell.Utility

# Set the URL and payload for the POST request
$WebRequestParams = @{
    Uri = "https://z2w55sggr4.execute-api.us-east-1.amazonaws.com/v1/mypath"
    Method = "POST"
    Headers = @{
        "x-api-key" = "<API_KEY>"
    }
    ContentType = "application/json"
}


# Execute the POST request and store the response
$response = Invoke-WebRequest @WebRequestParams

# Define the delimiter character
$delimiter = "\\n"

# Parse the returned string by the delimiter character
$parts = $response -split $delimiter

# Output the parsed parts
$parts.Replace('"', '')
