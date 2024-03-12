##################################################################################
### first, create the EventBridge Schedule

resource "aws_iam_role" "national_day_scheduler_role" {
  name               = "national_day_scheduler_role"
  description        = "The IAM role for the EventBridge Scheduler to assume"
  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "scheduler.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}

# define the policy document that will apply to the IAM role (best practice to not use heredoc / jsonencode)
data "aws_iam_policy_document" "national_day_scheduler_policy_document" {
  statement {
    sid = "1"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      aws_lambda_function.store_national_day_lambda.arn
    ]
  }
}

resource "aws_iam_policy" "national_day_scheduler_iam_policy" {
  name        = "national_day_scheduler_iam_policy"
  description = "The policy that will apply to the EventBridge Scheduler Role"
  policy      = data.aws_iam_policy_document.national_day_scheduler_policy_document.json
}

# what policy will define the permissions associated with the IAM role above
resource "aws_iam_role_policy_attachment" "national_day_policy_attachment" {
  policy_arn = aws_iam_policy.national_day_scheduler_iam_policy.arn
  role       = aws_iam_role.national_day_scheduler_role.name
}

# create the event bridge schedule to pull the national day of holidays
resource "aws_scheduler_schedule" "national_day_schedule" {
  name        = "national_day_schedule"
  description = "The EventBridge Scedule that will trigger the store_national_day Lambda, scheduled via cron syntax"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 10 * * ? *)" # run every day at 10AM UTC, cron syntax

  target {
    arn = aws_lambda_function.store_national_day_lambda.arn # arn of the lambda

    role_arn = aws_iam_role.national_day_scheduler_role.arn # role that allows scheduler to start the task

    retry_policy {
      maximum_retry_attempts = 0 # don't retry
    }
  }
}

##################################################################################
### next, we create the lambda and all associated roles/policies/applications

# what role will the lambda act under
resource "aws_iam_role" "national_day_lambda_role" {
  name               = "national_day_lambda_role"
  description        = "The IAM role for the store_national_day lambda to act under"
  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "lambda.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}

# define the policy document that will apply to the IAM role (best practice to not use heredoc / jsonencode)
data "aws_iam_policy_document" "national_day_lambda_policy_document" {
  statement {
    sid = "1"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }

  statement {
    sid = "2"

    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]

    resources = [
      aws_s3_bucket.national_day_of_holidays.arn,
      join("", [aws_s3_bucket.national_day_of_holidays.arn, "/*"]) # allow all objects in the bucket
    ]
  }
}

# what policy will define the permissions associated with the IAM role above
resource "aws_iam_policy" "national_day_lambda_iam_policy" {
  name        = "national_day_lambda_iam_policy"
  description = "The policy that will attach to the lambda role. Governs what our lambda can actually do to other aws services"
  policy      = data.aws_iam_policy_document.national_day_lambda_policy_document.json
}

# attach the policy to the role
resource "aws_iam_role_policy_attachment" "national_day_lamda_policy_attachment" {
  role       = aws_iam_role.national_day_lambda_role.name
  policy_arn = aws_iam_policy.national_day_lambda_iam_policy.arn
}

# zip the common python env requirments to facilitate a lambda layer
data "archive_file" "lambda_layer_zip" {
  type        = "zip"
  output_path = "${path.module}/.terraform/archive_files/lambda_layer.zip"
  source_dir  = "${path.module}/national_day_of_venv/lambda_layer_site_packages/"
}

# zip the lambda function scripts and their dependencies to allow upload to aws lambda
data "archive_file" "store_national_day_lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/.terraform/archive_files/store_national_day.zip"
  source_dir  = "${path.module}/store_national_day_lambda_function/"
}

data "archive_file" "retrieve_national_days_lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/.terraform/archive_files/retrieve_national_days.zip"
  source_dir  = "${path.module}/retrieve_national_days_lambda_function/"
}

# create the lambda layer
resource "aws_lambda_layer_version" "national_day_of_lambda_layer" {
  layer_name       = "national_day_of_lambda_layer"
  description      = "The python environment dependencies for the store_national_day, retrieve_national_days, and retrieve_national_day_image lambda functions"
  filename         = data.archive_file.lambda_layer_zip.output_path
  source_code_hash = data.archive_file.lambda_layer_zip.output_base64sha256


  compatible_runtimes = ["python3.12"]
  depends_on = [
    data.archive_file.lambda_layer_zip,
  ]
}

# create the store_national_day lambda resource
resource "aws_lambda_function" "store_national_day_lambda" {
  function_name    = "store_national_day"
  description      = "Lambda function to grab the various 'National Day of...' holidays for today from nationaltoday.com, and store it in s3 (along with the images)"
  role             = aws_iam_role.national_day_lambda_role.arn
  filename         = data.archive_file.store_national_day_lambda_zip.output_path
  handler          = "store_national_day.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["x86_64"]
  timeout          = 10
  depends_on       = [aws_iam_role_policy_attachment.national_day_lamda_policy_attachment]
  layers           = [aws_lambda_layer_version.national_day_of_lambda_layer.arn]
  source_code_hash = data.archive_file.store_national_day_lambda_zip.output_base64sha256 # ensures terraform recognizes changed to zip payload as changes
}

# create the retrieve_national_days lambda resource
resource "aws_lambda_function" "retrieve_national_days_lambda" {
  function_name    = "retrieve_national_days"
  description      = "Lambda function to retrieve the various 'National Day of...' holidays for today from s3, and return it as a json response"
  role             = aws_iam_role.national_day_lambda_role.arn
  filename         = data.archive_file.retrieve_national_days_lambda_zip.output_path
  handler          = "retrieve_national_days.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["x86_64"]
  timeout          = 10
  depends_on       = [aws_iam_role_policy_attachment.national_day_lamda_policy_attachment]
  layers           = [aws_lambda_layer_version.national_day_of_lambda_layer.arn]
  source_code_hash = data.archive_file.retrieve_national_days_lambda_zip.output_base64sha256 # ensures terraform recognizes changed to zip payload as changes
}


##################################################################################
### next, we create the s3 bucket to store the national holidays
resource "aws_s3_bucket" "national_day_of_holidays" {
  bucket = "national-day-of-holidays"
}
