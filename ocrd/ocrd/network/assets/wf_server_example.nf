@Grab(group='org.springframework.boot', module='spring-boot-starter-amqp', version='2.2.2.RELEASE')
import org.springframework.amqp.core.*
import org.springframework.amqp.rabbit.connection.CachingConnectionFactory
import org.springframework.amqp.rabbit.core.RabbitAdmin
import org.springframework.amqp.rabbit.listener.SimpleMessageListenerContainer
import org.springframework.amqp.rabbit.listener.api.*
import java.io.BufferedWriter
import java.io.OutputStreamWriter
import java.nio.charset.Charset
nextflow.enable.dsl=2

// These parameters can also be overwritten with values passed from the CLI
// when executing this script, i.e., --processing_server_address address
params.processing_server_address = "localhost:8080"
params.mets = "/home/mm/Desktop/example_ws/data/mets.xml"
// This is the entry point for the first ocr-d processor call in the Workflow
params.input_file_grp = "OCR-D-IMG"

params.rmq_address = "localhost:5672"
params.rmq_username = "default-consumer"
params.rmq_password = "default-consumer"
params.rmq_exchange = "ocrd-network-default"


log.info """\
  O C R - D - W O R K F L O W - W E B A P I - 1
  ======================================================
  processing_server_address : ${params.processing_server_address}
  mets                      : ${params.mets}
  input_file_grp            : ${params.input_file_grp}
  """
  .stripIndent()


// This global variable is used to track the status of 
// the previous process job in the when block of the current process job
job_status_flag = "NONE"


// RabbitMQ related globals
rmq_uri = "amqp://${params.rmq_username}:${params.rmq_password}@${params.rmq_address}"
println(rmq_uri)

def produce_job_input_json(input_grp, output_grp, page_id, ocrd_params){
  // TODO: Using string builder should be more computationally efficient
  def json_body = """{"path": "${params.mets}","""
  if (input_grp != null)
    json_body = json_body + """ "input_file_grps": ["${input_grp}"]"""
  if (output_grp != null)
    json_body = json_body + """, "output_file_grps": ["${output_grp}"]"""
  if (page_id != null)
    json_body = json_body + """, "page_id": ${page_id}"""
  if (ocrd_params != null)
    json_body = json_body + """, "parameters": ${ocrd_params}"""
  else
    json_body = json_body + """, "parameters": {}"""

  json_body = json_body + """}"""
  return json_body
}

def post_processing_job(ocrd_processor, input_grp, output_grp, page_id, ocrd_params){
  def post_connection = new URL("http://${params.processing_server_address}/processor/${ocrd_processor}").openConnection()
  post_connection.setDoOutput(true)
  post_connection.setRequestMethod("POST")
  post_connection.setRequestProperty("accept", "application/json")
  post_connection.setRequestProperty("Content-Type", "application/json")

  def json_body = produce_job_input_json(input_grp, output_grp, page_id, ocrd_params)
  println(json_body)

  def httpRequestBodyWriter = new BufferedWriter(new OutputStreamWriter(post_connection.getOutputStream()))
  httpRequestBodyWriter.write(json_body)
  httpRequestBodyWriter.close()

  def response_code = post_connection.getResponseCode()
  println("Response code: " + response_code)
  if (response_code.equals(200)){
    def json = post_connection.getInputStream().getText()
    println("ResponseJSON: " + json)
  }
}

def configure_queue_listener(result_queue_name){
  cf = new CachingConnectionFactory(new URI(rmq_uri))
  def rmq_admin = new RabbitAdmin(cf)
  def rmq_exchange = new DirectExchange(params.rmq_exchange, false, false)
  rmq_admin.declareExchange(rmq_exchange)

  def rmq_queue = new Queue(result_queue_name, false)
  rmq_admin.declareQueue(rmq_queue)
  rmq_admin.declareBinding(BindingBuilder.bind(rmq_queue).to(rmq_exchange).withQueueName())

  def listener = new SimpleMessageListenerContainer()
  listener.setConnectionFactory(cf)
  listener.setQueues(rmq_queue)
  listener.setMessageListener(new ChannelAwareMessageListener() {
    @Override
    void onMessage(Message message, com.rabbitmq.client.Channel channel) {
      println "Message received ${new Date()}"
      // println (message)
      def delivery_tag = message.getMessageProperties().getDeliveryTag()
      def consumer_tag = message.getMessageProperties().getConsumerTag()
      println "Consumer tag: ${consumer_tag}"
      println "Delivery tag: ${delivery_tag}"
      job_status = find_job_status(parse_body(message.getBody()))
      println "JobStatus: ${job_status}"
      // Overwrites the global status flag
      job_status_flag = job_status
      channel.basicAck(delivery_tag, false)
      // channel.basicCancel(consumer_tag)
      println "Trying to stop listener"
      // channel.close(0, "Closing the channel after successful consumption.")
      listener.stop()
      println "After stop listener"
    }
    String parse_body(byte[] bytes) {
      if (bytes) {
        new String(bytes, Charset.forName('UTF-8'))
      }
    }
    String find_job_status(String message_body){
      // TODO: Use Regex
      if (message_body.contains("SUCCESS")){
        return "SUCCESS"
      } 
      else if (message_body.contains("FAILED")){
        return "FAILED"
      }
      else if (message_body.contains("RUNNING")){
        return "RUNNING"
      }
      else if (message_body.contains("QUEUED")){
        return "QUEUED"
      }
      else {
        return "NONE"
      }
    }
  })

  return listener
}

def exec_block_logic(ocrd_processor_str, input_dir, output_dir, page_id, ocrd_params){
  String result_queue = "${ocrd_processor_str}-result"
  post_processing_job(ocrd_processor_str, input_dir, output_dir, null, null)
  job_status_flag = "INITIALIZED"
  def listener = configure_queue_listener(result_queue)
  // The job_status_flag is with value "INITIALIZED" here
  println "Starting listening, flag: ${job_status_flag}"
  listener.start()
  // The job_status_flag must be with value "SUCCESS" or "FAILED" here
  println "Ended listening, flag: ${job_status_flag}"

  // The job_status_flag gets overwritten inside the onMessage 
  // method when a message is consumed from the result queue
  return job_status_flag
}

process binarize {
  maxForks 1

  input:
    val input_dir
    val output_dir

  output:
    val output_dir
    val job_status

  exec:
    job_status = exec_block_logic("ocrd-cis-ocropy-binarize", input_dir, output_dir, null, null)
    println "binarize returning flag: ${job_status}"
}

process crop {
  maxForks 1

  input:
    val input_dir
    val output_dir
    val prev_job_status

  when:
    prev_job_status == "SUCCESS"

  output:
    val output_dir
    val job_status

  exec:
    job_status = exec_block_logic("ocrd-anybaseocr-crop", input_dir, output_dir, null, null)
    println "crop returning flag: returning job status: ${job_status}"
}

workflow {

  main:
    binarize(params.input_file_grp, "OCR-D-BIN")
    crop(binarize.out[0], "OCR-D-CROP", binarize.out[1])
}
