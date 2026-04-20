//
//  ProductListViewController.swift
//  apiCallingPractice
//
//  Created by BS1101 on 15/5/23.
//

import UIKit
import WebKit

class ProductListViewController: UIViewController {
    
    // Provide the URL string of the webpage to load. Set this before presenting/pushing the view controller.
    var webURLString: String?

    /// Convenience configuration method so callers can simply pass a link.
    /// - Parameter urlString: The string URL to load in the embedded WKWebView.
    func configure(with urlString: String) {
        self.webURLString = urlString
    }

    @IBOutlet weak var streamLitWeb: WKWebView!
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Load the provided URL if available, otherwise fall back to localhost
        if let webURLString, let url = URL(string: webURLString) {
            let request = URLRequest(url: url)
            streamLitWeb?.load(request)
        } else if webURLString == nil {
            // Fallback to localhost if no URL provided
            if let localhostURL = URL(string: "https://lybasiddiqui-customer-churn-project-app-sh7p8f.streamlit.app/") {
                let request = URLRequest(url: localhostURL)
                streamLitWeb?.load(request)
            }
        } else {
            // Provided string was not a valid URL
            print("Invalid URL string provided: \(webURLString ?? "nil")")
        }

        APIManager.shared.fetchProducts { response in
            switch response{
            case .success(let products):
                print(products)
            case .failure(let error):
                print(error)
            }
        }
        
        
        /*
         // MARK: - Navigation
         
         // In a storyboard-based application, you will often want to do a little preparation before navigation
         override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
         // Get the new view controller using segue.destination.
         // Pass the selected object to the new view controller.
         }
         */
        
    }
}
