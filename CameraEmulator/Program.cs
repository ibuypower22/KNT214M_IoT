using System;
using System.IO;
using System.Drawing;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using AForge.Video;
using AForge.Video.DirectShow;

class Program
{
    private static VideoCaptureDevice _webcam;
    private static Bitmap _currentFrame;
    private static readonly HttpClient _httpClient = new HttpClient();
    private static string id = "";
    private static string host = "";
    private static string _url = "http://{0}/api/addimage/";
    private const int _interval = 100;
    private static readonly object locker = new object();

    static async Task Main(string[] args)
    {
        Console.WriteLine("Enter host: ");
        host = Console.ReadLine();

        Console.WriteLine("Enter your id: ");
        id = Console.ReadLine();

        var videoDevices = new FilterInfoCollection(FilterCategory.VideoInputDevice);

        if (videoDevices.Count == 0)
        {
            Console.WriteLine("No webcam found.");
            return;
        }

        _webcam = new VideoCaptureDevice(videoDevices[0].MonikerString);
        _webcam.NewFrame += new NewFrameEventHandler(OnNewFrame);
        _webcam.Start();

        while (true)
        {
            byte[] imageBytes = null;

            lock (locker)
            {
                if (_currentFrame != null)
                {
                    using (var memoryStream = new MemoryStream())
                    {
                        _currentFrame.Save(memoryStream, System.Drawing.Imaging.ImageFormat.Jpeg);
                        imageBytes = memoryStream.ToArray();
                    }
                }
            }

            if (imageBytes != null)
            {
                await SendImageAsync(imageBytes);
            }

            await Task.Delay(_interval); // wait for 1 second
        }
    }

    private static void OnNewFrame(object sender, NewFrameEventArgs eventArgs)
    {
        lock (locker)
        {
            if (_currentFrame != null)
            {
                _currentFrame.Dispose();
            }

            _currentFrame = (Bitmap)eventArgs.Frame.Clone();
        }
    }

    private static async Task SendImageAsync(byte[] imageBytes)
    {
        using (var content = new MultipartFormDataContent())
        {
            // Prepare the image content as a file in the multipart form-data
            var imageContent = new ByteArrayContent(imageBytes);
            imageContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("image/jpeg");
            content.Add(imageContent, "image", "webcam_image.jpg");

            try
            {
                var route = string.Format(_url, host) + id;
                var response = await _httpClient.PostAsync(route, content);
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Image sent successfully.");
                }
                else
                {
                    Console.WriteLine($"Failed to send image. Status: {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }
    }
}
