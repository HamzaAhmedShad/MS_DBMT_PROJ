//
//  ProductListViewController.swift
//  apiCallingPractice
//
//  Created by BS1101 on 15/5/23.
//

import UIKit

class ProductListViewController: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
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
